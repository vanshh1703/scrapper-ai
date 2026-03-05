import asyncio
from typing import List
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.product import PriceSheet, PriceSheetRow, PriceSheetPincode
from services.comparison import search_and_compare
import logging
import re

async def generate_price_sheet(db: Session, user_id: int, sheet_name: str, models: List[str] = None, brand_search: bool = False, query: str = None):
    """
    Generate a full price sheet with autofilled details for each model and retailer.
    """
    if models is None:
        models = []
        
    # Brand Discovery Phase
    if brand_search and query:
        print(f"Starting brand discovery for: {query}")
        discovery_data = await search_and_compare(db, query, user_id)
        raw_results = discovery_data.get('results', [])
        
        # Extract unique product names (simplified normalization)
        found_models = set()
        brand_query = query.strip().upper()
        for res in raw_results:
            name = res.get('product_name', '').upper()
            if name and "UNKNOWN" not in name:
                # Remove common noise but keep storage and model series
                # Preserve formats like 4/64, 8/128, (X115), etc.
                # Remove generic stuff like 'Smartphone', 'Mobile', etc.
                clean_name = re.sub(r'(?:SMARTPHONE|MOBILE|PHONE|CELLULAR)\b', '', name, flags=re.IGNORECASE)
                # Ensure it starts with the brand name for consistency
                if brand_query not in clean_name:
                    clean_name = f"{brand_query} {clean_name}"
                
                # Further cleanup: remove excessive whitespace
                clean_name = " ".join(clean_name.split())
                
                if len(clean_name) > 8:
                    found_models.add(clean_name)
        
        models = sorted(list(found_models))[:25] # Order alphabetically and limit
        print(f"Discovered {len(models)} models for brand {query}")

    sheet = PriceSheet(name=sheet_name, user_id=user_id)
    db.add(sheet)
    db.commit()
    db.refresh(sheet)
    
    PINCODES = [
        ("DELHI", "110027"), ("EOK", "110065"), ("GURGAON", "122001"),
        ("UP", "201002"), ("KOTA", "324001"), ("CHANDIGARH", "160015"),
        ("AMRITSAR", "143501"), ("MOHALI", "140306"), ("KOLKATA", "700104"),
        ("PUNE", "411001"), ("MUMBAI", "400069")
    ]
    
    CIF_FACTOR = 91.20 # Based on the spreadsheet image header
    RETAILERS = ["Amazon India", "Flipkart", "Vijay Sales", "Jio Mart"]
    
    # 1. Search for all models in parallel
    print(f"Searching for {len(models)} models in parallel...")
    search_tasks = [search_and_compare(db, m, user_id, commit=False) for m in models]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    # Commit search history once
    db.commit()

    for i, model_name in enumerate(models):
        try:
            res = search_results[i]
            if isinstance(res, Exception):
                logging.error(f"Search failed for {model_name}: {res}")
                error_row = PriceSheetRow(sheet_id=sheet.id, model_name=model_name, remark=f"Search Error: {str(res)[:20]}")
                db.add(error_row)
                continue

            all_results = res.get('results', [])
            
            # Group results by retailer
            retailer_results = {r: [] for r in RETAILERS}
            for r_res in all_results:
                site = r_res.get('site')
                if site in retailer_results:
                    retailer_results[site].append(r_res)

            # Find overall best (cheapest available) for pincode data
            best_overall = None
            in_stock = [r_res for r_res in all_results if r_res.get('current_price', 0) > 0 and r_res.get('availability') != "Out of Stock"]
            if in_stock:
                best_overall = min(in_stock, key=lambda x: x['current_price'])
            
            # 2. Create one row per retailer for this model
            for retailer_name in RETAILERS:
                matches = retailer_results[retailer_name]
                best_match = None
                
                if matches:
                    model_keywords = set(re.findall(r'\w+', model_name.lower()))
                    # Keywords that usually indicate a wrong product type (accessory)
                    accessory_keywords = {'case', 'cover', 'glass', 'strap', 'band', 'protector', 'cable', 'adapter', 'charging'}
                    
                    scored = []
                    for m in matches:
                        p_name = m.get('product_name', '').lower()
                        # Base score: number of matching model keywords
                        score = sum(2 for w in model_keywords if w in p_name)
                        
                        # Penalty for accessory keywords if they aren't in the model name
                        for ak in accessory_keywords:
                            if ak in p_name and ak not in model_name.lower():
                                score -= 10
                                
                        # Penalty for 'for' or 'compatible'
                        if any(k in p_name for k in ['for ', ' compatible', 'designed for']):
                            score -= 8
                            
                        # Bonus for starting with the brand or model name
                        first_word = model_name.split()[0].lower()
                        if p_name.startswith(first_word):
                            score += 5
                            
                        scored.append({"res": m, "score": score})
                    
                    if scored:
                        # Sort by score descending, then by price ascending
                        scored.sort(key=lambda x: (-x['score'], x['res']['current_price']))
                        if scored[0]['score'] > 0:
                            best_match = scored[0]['res']

                # Initialize row data
                avail = best_match.get('availability', 'OOS') if best_match else "OOS"
                # Detect Brand and Channel Dynamically
                lower_model = model_name.lower()
                
                if "samsung" in lower_model or "galaxy" in lower_model or "tab" in lower_model:
                    channel_brand = "SAMSUNG"
                elif "apple" in lower_model or "iphone" in lower_model or "airpods" in lower_model:
                    channel_brand = "APPLE"
                elif "dyson" in lower_model:
                    channel_brand = "DYSON"
                elif "sony" in lower_model:
                    channel_brand = "SONY"
                else:
                    # Fallback: Use the first word of the model name as the brand
                    channel_brand = model_name.split()[0].upper()

                # If the match score was too low or it's clearly a wrong price for a phone
                if best_match:
                    price = best_match.get('current_price', 0)
                    # For Apple/Samsung phones, apply strict price floors
                    if channel_brand in ["APPLE", "SAMSUNG"] and not any(k in lower_model for k in ["tab", "watch", "bud", "pencil"]):
                        if channel_brand == "APPLE" and "iphone" in lower_model and price < 20000:
                            avail = "WRONG_PROD"
                        elif channel_brand == "SAMSUNG" and price < 10000:
                            avail = "WRONG_PROD"
                    # For Dyson, vacuums and dryers are expensive, but tools/sub-parts can be cheap
                    elif channel_brand == "DYSON" and price < 2000:
                        avail = "WRONG_PROD"

                row = PriceSheetRow(
                    sheet_id=sheet.id,
                    model_name=model_name,
                    retailer=retailer_name,
                    channel=channel_brand,
                    remark=avail,
                    mop_offline=0, cif_offline=0, mop_online=0,
                    secure_packaging=0, offer_handling=0, corp_fees=0,
                    coupon=0, bank_hdfc=0, bank_icici=0,
                    swipe_amount=0, cashback_hdfc=0, cashback_icici=0, cashback_emi=0,
                    landing_price=0, emi_landing=0, cif_cost_today=0
                )

                if best_match:
                    price = best_match.get('current_price', 0)
                    row.mop_online = price
                    row.product_url = best_match.get('url', '')
                    
                    # Packaging fees
                    if "flipkart" in retailer_name.lower():
                        row.secure_packaging = 99
                    
                    # Bank Offers
                    if price > 50000:
                        row.bank_hdfc = 2000
                        row.cashback_hdfc = 1000
                    
                    row.swipe_amount = row.mop_online + row.secure_packaging - row.bank_hdfc
                    row.landing_price = row.swipe_amount - row.cashback_hdfc
                    row.emi_landing = row.landing_price
                    row.cif_cost_today = int(row.landing_price / CIF_FACTOR) if CIF_FACTOR > 0 else 0
                    
                    delivery = best_match.get('delivery_info', '')
                    colors = best_match.get('colors', '')
                    remark_pts = [avail]
                    if delivery: remark_pts.append(f"Del: {delivery}")
                    if colors: remark_pts.append(f"Colors: {colors}")
                    row.remark = " | ".join(remark_pts)
                
                db.add(row)

            # 3. Populate Pincode Sheets (once per model, using best overall result)
            if best_overall:
                avail = best_overall.get('availability', 'In Stock')
                delivery = best_overall.get('delivery_info', '')
                colors = best_overall.get('colors', '')
                base_del_days = 2
                
                for city, pin in PINCODES:
                    jitter = 0 if city in ["DELHI", "MUMBAI", "EOK"] else random.randint(1, 2)
                    del_date = (datetime.now() + timedelta(days=base_del_days + jitter)).strftime("%d %b")
                    
                    pin_row = PriceSheetPincode(
                        sheet_id=sheet.id,
                        model_name=model_name,
                        pincode=pin,
                        city_name=city,
                        availability="In Stock" if avail != "OOS" else "OOS",
                        delivery_date=del_date if avail != "OOS" else "N/A",
                        colors=colors if avail != "OOS" else "N/A"
                    )
                    db.add(pin_row)

        except Exception as e:
            logging.error(f"Error generating row for {model_name}: {e}")
            error_row = PriceSheetRow(sheet_id=sheet.id, model_name=model_name, remark=f"Error: {str(e)[:20]}")
            db.add(error_row)
    
    db.commit()
    db.refresh(sheet)
    return sheet
