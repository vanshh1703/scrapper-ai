import asyncio
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper
from scrapers.vijaysales import VijaySalesScraper
from scrapers.jiomart import JioMartScraper
from sqlalchemy.orm import Session
from models.product import Product, PriceHistory
from models.history import SearchHistory
from services.decision import get_purchase_decision

async def search_and_compare(db: Session, query: str, user_id: int, commit: bool = True):
    import sys
    print("search_and_compare START:", query)
    sys.stdout.flush()
    
    amazon = AmazonScraper()
    flipkart = FlipkartScraper()
    vijaysales = VijaySalesScraper()
    jiomart = JioMartScraper()
    
    # Run all scrapers in parallel
    print(f"[{query}] Searching across 4 retailers...")
    res_list = await asyncio.gather(
        amazon.scrape(query),
        flipkart.scrape(query),
        vijaysales.scrape(query),
        jiomart.scrape(query)
    )
        
    results = []
    for r in res_list:
        if isinstance(r, list):
            results.append(r)
    
    all_products = []
    for r in results:
        if isinstance(r, list):
            all_products.extend(r)
        
    print("Total products found:", len(all_products))
    sys.stdout.flush()
    # Sort by lowest price
    all_products.sort(key=lambda x: x["current_price"])
    
    # FILTERING LOGIC: Exclude fakes and accessories if searching for a device
    EXCLUSION_KEYWORDS = ['for', 'compatible', 'replacement', 'clone', 'fake', 'copy', 'dummy', 'cover', 'case', 'protector', 'lens', 'strap', 'band', 'skin', 'glass', 'accessory', 'motherboard', 'mainboard', 'display', 'screen', 'battery', 'housing', 'camera module', 'flex cable', 'board', 'part', 'spare', 'unit', 'assembly', 'lcd', 'trimmer', 'shaver', 'epilator', 'hair', 'dryer', 'straightener', 'grooming']
    KNOWN_COMPETITORS = ['boat', 'noise', 'boult', 'ptron', 'zebronics', 'realme', 'oppo', 'oneplus', 'samsung', 'hammer', 'boult', 'mivi', 'truke', 'wings', 'apple']
    
    filtered_products = []
    query_lower = query.lower()
    
    # Identify the target brand from query
    target_brand = None
    if any(k in query_lower for k in ["apple", "iphone", "airpods"]): target_brand = "apple"
    elif any(k in query_lower for k in ["samsung", "galaxy"]): target_brand = "samsung"
    elif "dyson" in query_lower: target_brand = "dyson"
    
    for p in all_products:
        name_lower = p['product_name'].lower()
        price = p['current_price']
        
        # 1. Broad exclusion (case, cover, component parts, etc.)
        # ONLY exclude if the keyword is NOT in the query (e.g. if query is 'Dyson Dryer', don't exclude 'dryer')
        # Also relax for Dyson specific categories
        special_categories = []
        if target_brand == "dyson": special_categories = ["dryer", "hair", "vacuum", "air", "cleaner"]
        
        active_exclusions = [k for k in EXCLUSION_KEYWORDS if k not in query_lower and k not in special_categories]
        if any(f" {k} " in f" {name_lower} " or name_lower.endswith(f" {k}") or name_lower.startswith(f"{k} ") for k in active_exclusions):
             # Final safety: if query mentioned 'case' or 'cover', we allow it
             if not any(k in query_lower for k in ['case', 'cover', 'strap', 'screen', 'battery', 'motherboard']):
                print(f"Skipping accessory/component/fake/mismatch: {p['product_name']}")
                continue

        # 2. Competitive brand exclusion for premium searches
        if target_brand:
            # If we're searching for a specific brand, and the title contains another known brand name but NOT our target brand
            remaining_competitors = [cb for cb in KNOWN_COMPETITORS if cb != target_brand]
            if any(cb in name_lower for cb in remaining_competitors):
                if target_brand not in name_lower:
                    # Exception: Samsung often lists 'for iPhone' in its accessory titles, which is handled by EXCLUSION_KEYWORDS
                    print(f"Skipping competing brand: {p['product_name']}")
                    continue
            
            # 3. Strict Brand Enforcement for Devices
            if any(k in query_lower for k in ["airpods", "iphone", "galaxy", "s24", "s23", "s25", "flip", "fold"]):
                if target_brand not in name_lower and not (target_brand == "samsung" and "galaxy" in name_lower):
                    print(f"Skipping product without brand keywords: {p['product_name']}")
                    continue
                
                # 4. Price Floors for Premium Devices (India)
                if target_brand == "apple":
                    if "airpods pro" in query_lower and price < 15000:
                        continue
                    if "airpods" in query_lower and price < 8000:
                        continue
                    if "iphone" in query_lower and price < 30000 and "se" not in name_lower:
                        continue
                elif target_brand == "samsung":
                    if any(k in query_lower for k in ["s24", "s23", "s22", "fold", "flip"]) and price < 35000:
                        print(f"Skipping suspicious price for Samsung Premium: {p['product_name']} ({price})")
                        continue
                    if "galaxy" in query_lower and price < 8000 and "tab" not in query_lower:
                        # Budget M-series/A-series are above 8-10k. Components/Parts are often 1-5k.
                        print(f"Skipping suspicious price for Samsung Device: {p['product_name']} ({price})")
                        continue

        filtered_products.append(p)
    
    all_products = filtered_products
    
    if not all_products:
        return {"query": query, "results": []}
        
    # Get the cheapest product with stock
    in_stock = [p for p in all_products if p["current_price"] > 0]
    cheapest = in_stock[0] if in_stock else all_products[0]
    
    # Save search history
    db_search = SearchHistory(user_id=user_id, query=query)
    db.add(db_search)
    if commit:
        db.commit()
    
    final_output = []
    max_price = max((p["current_price"] for p in all_products if p["current_price"] > 0), default=0)
    
    for item in all_products:
        if item["current_price"] <= 0:
            continue
            
        # Update or Create Product
        # 1. Check existing in DB
        db_prod = db.query(Product).filter(Product.url == item["url"]).first()
        
        # 2. Check if it's already in the session but not committed yet (for parallel tasks)
        if not db_prod:
            for obj in db.new:
                if isinstance(obj, Product) and obj.url == item["url"]:
                    db_prod = obj
                    break
                    
        if not db_prod:
            db_prod = Product(**item)
            db.add(db_prod)
            if commit:
                try:
                    db.commit()
                    db.refresh(db_prod)
                except Exception as e:
                    db.rollback()
                    # Final check: maybe another task committed it in the meantime
                    db_prod = db.query(Product).filter(Product.url == item["url"]).first()
                    if not db_prod: raise e
        else:
            # Update existing
            db_prod.current_price = item["current_price"]
            db_prod.availability = item["availability"]
            db_prod.delivery_info = item.get("delivery_info")
            db_prod.colors = item.get("colors")
            if item["rating"]:
                db_prod.rating = item["rating"]
            if commit:
                db.commit()
                db.refresh(db_prod)
            
        # Add to PriceHistory
        p_history = PriceHistory(product_id=db_prod.id, price=item["current_price"])
        db.add(p_history)
        if commit:
            db.commit()
        
        # Calculate derived fields
        decision = get_purchase_decision(db, db_prod.id)
        is_cheapest = (item == cheapest)
        savings_percent = round(((max_price - item["current_price"]) / max_price) * 100) if max_price > 0 else 0
        
        item_copy = dict(item)
        item_copy["id"] = db_prod.id
        item_copy["cheapest"] = is_cheapest
        item_copy["decision"] = decision
        item_copy["savings_percent"] = savings_percent
        final_output.append(item_copy)
        
    return {
        "query": query,
        "results": final_output
    }
