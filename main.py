from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import os
from typing import List, Dict, Optional
from pathlib import Path

app = FastAPI(title="Purchase Order API", description="API to read and manage Purchase Orders from CSV")

# Path to CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "purchase_orders.csv")

# Helper function to check if CSV exists
def check_csv_exists():
    if not os.path.exists(CSV_FILE_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found. Please run generatePOData.js first.")

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Purchase Order API",
        "endpoints": {
            "all_orders": "/api/orders",
            "order_by_id": "/api/orders/{po_number}",
            "download_csv": "/api/download",
            "statistics": "/api/statistics",
            "filter": "/api/orders?vendor=&status="
        }
    }

@app.get("/api/orders")
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vendor: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """Get all Purchase Orders with pagination and filtering"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Apply filters
        if vendor:
            df = df[df['Vendor'].str.contains(vendor, case=False, na=False)]
        if status:
            df = df[df['Status'].str.contains(status, case=False, na=False)]
        
        # Pagination
        total = len(df)
        df = df.iloc[skip:skip + limit]
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(df),
            "orders": df.to_dict(orient="records")
        }
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{po_number}")
async def get_order_by_po(po_number: str) -> Dict:
    """Get a specific Purchase Order by PO Number"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        order = df[df['PO Number'] == po_number]
        if order.empty:
            raise HTTPException(status_code=404, detail=f"PO Number {po_number} not found")
        
        return {"order": order.to_dict(orient="records")[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics() -> Dict:
    """Get statistics about Purchase Orders"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        stats = {
            "total_orders": len(df),
            "total_amount": float(df['Grand Total'].sum()),
            "average_order_value": float(df['Grand Total'].mean()),
            "by_status": df['Status'].value_counts().to_dict(),
            "by_vendor": df['Vendor'].value_counts().to_dict(),
            "by_department": df['Department'].value_counts().to_dict(),
            "by_currency": df['Currency'].value_counts().to_dict(),
            "approval_status_breakdown": df['Approval Status'].value_counts().to_dict()
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
async def download_csv():
    """Download the CSV file"""
    try:
        check_csv_exists()
        return FileResponse(
            path=CSV_FILE_PATH,
            filename="purchase_orders.csv",
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vendors")
async def get_unique_vendors() -> Dict:
    """Get list of unique vendors"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        vendors = df['Vendor'].unique().tolist()
        return {"vendors": vendors, "count": len(vendors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/departments")
async def get_unique_departments() -> Dict:
    """Get list of unique departments"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        departments = df['Department'].unique().tolist()
        return {"departments": departments, "count": len(departments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def export_filtered_data(
    vendor: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """Export filtered data"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if vendor:
            df = df[df['Vendor'].str.contains(vendor, case=False, na=False)]
        if status:
            df = df[df['Status'].str.contains(status, case=False, na=False)]
        
        return {"exported_records": len(df), "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
