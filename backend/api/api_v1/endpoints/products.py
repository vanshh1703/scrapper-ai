from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, List
import logging

from core.database import get_db
from models.user import User
from models.history import SearchHistory, PriceAlert
from models.product import Product, PriceHistory
from utils.dependencies import get_current_active_user
from services.comparison import search_and_compare
from schemas.product import ProductRead

router = APIRouter()

@router.get("/search")
def search_products(
    query: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search a product across multiple sites. Limit based on subscription plan.
    """
    if current_user.role == "free" and current_user.searches_today >= 50:
        raise HTTPException(status_code=403, detail="Free tier limit reached. Please upgrade to Pro.")
        
    current_user.searches_today += 1
    db.commit()
    
    # Run in a separate thread/loop via asyncio.run to ensure ProactorEventLoop on Windows
    # This bypasses Uvicorn's default SelectorEventLoop which lacks subprocess support.
    try:
        import asyncio
        return asyncio.run(search_and_compare(db, query, current_user.id))
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        raise HTTPException(status_code=400, detail=str(err_msg))

from schemas.product import PriceSheetCreate, PriceSheetRead
from services.sheet_generator import generate_price_sheet

@router.post("/sheets/generate", response_model=PriceSheetRead)
def generate_sheet_endpoint(
    sheet_data: PriceSheetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Generate a new price sheet for a list of models.
    """
    try:
        import asyncio
        sheet = asyncio.run(generate_price_sheet(
            db=db, 
            user_id=current_user.id, 
            sheet_name=sheet_data.name, 
            models=sheet_data.models,
            brand_search=sheet_data.brand_search,
            query=sheet_data.query
        ))
        return sheet
    except Exception as e:
        import traceback
        logging.error(f"Sheet Gen Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sheets/{sheet_id}", response_model=PriceSheetRead)
def get_sheet(
    sheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific price sheet by ID.
    """
    from models.product import PriceSheet
    sheet = db.query(PriceSheet).filter(PriceSheet.id == sheet_id, PriceSheet.user_id == current_user.id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet

@router.get("/sheets", response_model=List[PriceSheetRead])
def get_user_sheets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all price sheets of the current user.
    """
    from models.product import PriceSheet
    return db.query(PriceSheet).filter(PriceSheet.user_id == current_user.id).all()

@router.get("/sheets/{sheet_id}/export")
def export_sheet_to_excel(
    sheet_id: int,
    retailer: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Export a price sheet to an Excel file.
    """
    from models.product import PriceSheet
    import pandas as pd
    import io
    from fastapi.responses import StreamingResponse

    sheet = db.query(PriceSheet).filter(PriceSheet.id == sheet_id, PriceSheet.user_id == current_user.id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")

    # Prepare data for Excel
    data = []
    filtered_rows = sheet.rows
    if retailer and retailer != "All":
        filtered_rows = [r for r in sheet.rows if r.retailer == retailer]

    for row in filtered_rows:
        data.append({
            "Model Name": row.model_name,
            "Brand Channel": row.channel,
            "Retailer": row.retailer,
            "MOP Offline": row.mop_offline,
            "CIF Offline": row.cif_offline,
            "MOP Online": row.mop_online,
            "Secure Pkg": row.secure_packaging,
            "Handling": row.offer_handling,
            "Corp Fees": row.corp_fees,
            "Coupon": row.coupon,
            "Bank HDFC": row.bank_hdfc,
            "Bank ICICI": row.bank_icici,
            "Swipe Amount": row.swipe_amount,
            "Cashback HDFC": row.cashback_hdfc,
            "Cashback ICICI": row.cashback_icici,
            "Cashback EMI": row.cashback_emi,
            "Landing Price": row.landing_price,
            "EMI Landing": row.emi_landing,
            "CIF Cost Today": row.cif_cost_today,
            "Remark": row.remark,
            "Product Link": row.product_url
        })

    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Price Sheet')
        
        # Also add Pincode sheet if data exists
        if sheet.pincodes:
            pin_data = []
            for pin in sheet.pincodes:
                pin_data.append({
                    "Model": pin.model_name,
                    "City": pin.city_name,
                    "Pincode": pin.pincode,
                    "Availability": pin.availability,
                    "Delivery Date": pin.delivery_date,
                    "Colors Available": pin.colors
                })
            df_pins = pd.DataFrame(pin_data)
            df_pins.to_excel(writer, index=False, sheet_name='Pincode Availability')

    output.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="PriceSheet_{sheet.id}.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.get("/dashboard")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    searches = db.query(SearchHistory).filter(SearchHistory.user_id == current_user.id).count()
    alerts = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id).count()
    
    return {
        "total_searches": searches,
        "saved_alerts": alerts,
        "plan": current_user.role,
        "searches_today": current_user.searches_today
    }
