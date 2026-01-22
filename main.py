from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
from typing import List, Dict, Optional
from pathlib import Path

app = FastAPI(title="Purchase Order API", description="API to read and manage Purchase Orders from CSV")

# Enable CORS for all origins (allow voice dashboard and other clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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
            "filter": "/api/orders?vendor=&status=",
            "voice_dashboard": "/dashboard"
        }
    }

@app.get("/dashboard")
async def get_voice_dashboard():
    """Serve the voice-enabled dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "voice-dashboard.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r') as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="Voice dashboard not found")

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

@app.get("/api/approval-summary")
async def get_approval_summary() -> Dict:
    """Get approval status summary with assigned personnel and grand total amounts"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Group by approval status
        approval_groups = df.groupby('Approval Status').agg({
            'Grand Total': ['sum', 'mean', 'count'],
            'Assigned To': lambda x: x.unique().tolist()
        }).round(2)
        
        summary = {}
        for approval_status in df['Approval Status'].unique():
            status_df = df[df['Approval Status'] == approval_status]
            summary[approval_status] = {
                "count": len(status_df),
                "total_amount": float(status_df['Grand Total'].sum()),
                "average_amount": float(status_df['Grand Total'].mean()),
                "assigned_to": status_df['Assigned To'].unique().tolist(),
                "orders": status_df[['PO Number', 'Vendor', 'Assigned To', 'Grand Total', 'Status', 'PO Date']].to_dict(orient='records')
            }
        
        return {
            "summary": summary,
            "grand_total_all_orders": float(df['Grand Total'].sum()),
            "total_orders": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assigned-to")
async def get_by_assigned_to(assigned_to: Optional[str] = None) -> Dict:
    """Get orders by who it's assigned to with grand total amounts"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if assigned_to:
            df = df[df['Assigned To'].str.contains(assigned_to, case=False, na=False)]
        
        result = {}
        for person in df['Assigned To'].unique():
            person_df = df[df['Assigned To'] == person]
            result[person] = {
                "orders_count": len(person_df),
                "grand_total": float(person_df['Grand Total'].sum()),
                "average_order_value": float(person_df['Grand Total'].mean()),
                "approval_status_breakdown": person_df['Approval Status'].value_counts().to_dict(),
                "orders": person_df[['PO Number', 'Vendor', 'Approval Status', 'Grand Total', 'Status']].to_dict(orient='records')
            }
        
        return {
            "by_assigned_to": result,
            "total_people": len(result),
            "grand_total_amount": float(df['Grand Total'].sum())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-department")
async def get_by_department(department: Optional[str] = None) -> Dict:
    """Get orders grouped by department with totals and metrics"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if department:
            df = df[df['Department'].str.contains(department, case=False, na=False)]
        
        result = {}
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            result[dept] = {
                "orders_count": len(dept_df),
                "grand_total": float(dept_df['Grand Total'].sum()),
                "average_order_value": float(dept_df['Grand Total'].mean()),
                "status_breakdown": dept_df['Status'].value_counts().to_dict(),
                "locations": dept_df['Location'].unique().tolist()
            }
        
        return {"by_department": result, "total_departments": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-location")
async def get_by_location(location: Optional[str] = None) -> Dict:
    """Get orders grouped by location with financial summary"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if location:
            df = df[df['Location'].str.contains(location, case=False, na=False)]
        
        result = {}
        for loc in df['Location'].unique():
            loc_df = df[df['Location'] == loc]
            result[loc] = {
                "orders_count": len(loc_df),
                "grand_total": float(loc_df['Grand Total'].sum()),
                "average_order_value": float(loc_df['Grand Total'].mean()),
                "departments": loc_df['Department'].unique().tolist(),
                "top_vendor": loc_df['Vendor'].value_counts().index[0] if not loc_df.empty else None
            }
        
        return {"by_location": result, "total_locations": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-payment-terms")
async def get_by_payment_terms(payment_terms: Optional[str] = None) -> Dict:
    """Get orders grouped by payment terms"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if payment_terms:
            df = df[df['Payment Terms'].str.contains(payment_terms, case=False, na=False)]
        
        result = {}
        for term in df['Payment Terms'].unique():
            term_df = df[df['Payment Terms'] == term]
            result[term] = {
                "orders_count": len(term_df),
                "grand_total": float(term_df['Grand Total'].sum()),
                "average_order_value": float(term_df['Grand Total'].mean()),
                "vendors": term_df['Vendor'].unique().tolist()
            }
        
        return {"by_payment_terms": result, "total_terms": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-currency")
async def get_by_currency(currency: Optional[str] = None) -> Dict:
    """Get orders grouped by currency"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if currency:
            df = df[df['Currency'].str.contains(currency, case=False, na=False)]
        
        result = {}
        for curr in df['Currency'].unique():
            curr_df = df[df['Currency'] == curr]
            result[curr] = {
                "orders_count": len(curr_df),
                "total_amount": float(curr_df['Grand Total'].sum()),
                "average_amount": float(curr_df['Grand Total'].mean()),
                "min_amount": float(curr_df['Grand Total'].min()),
                "max_amount": float(curr_df['Grand Total'].max())
            }
        
        return {"by_currency": result, "total_currencies": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-created-by")
async def get_by_created_by(created_by: Optional[str] = None) -> Dict:
    """Get orders created by specific person"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if created_by:
            df = df[df['Created By'].str.contains(created_by, case=False, na=False)]
        
        result = {}
        for person in df['Created By'].unique():
            person_df = df[df['Created By'] == person]
            result[person] = {
                "orders_created": len(person_df),
                "total_value": float(person_df['Grand Total'].sum()),
                "average_value": float(person_df['Grand Total'].mean()),
                "departments": person_df['Department'].unique().tolist(),
                "approval_statuses": person_df['Approval Status'].value_counts().to_dict()
            }
        
        return {"by_created_by": result, "total_creators": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/high-value-orders")
async def get_high_value_orders(min_amount: float = Query(5000, ge=0)) -> Dict:
    """Get orders with grand total above specified amount"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        df['Grand Total'] = pd.to_numeric(df['Grand Total'], errors='coerce')
        
        high_value = df[df['Grand Total'] >= min_amount].sort_values('Grand Total', ascending=False)
        
        return {
            "min_amount_filter": min_amount,
            "count": len(high_value),
            "total_value": float(high_value['Grand Total'].sum()),
            "average_value": float(high_value['Grand Total'].mean()),
            "orders": high_value[['PO Number', 'Vendor', 'Grand Total', 'Status', 'Approval Status']].to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pending-approvals")
async def get_pending_approvals() -> Dict:
    """Get all orders pending approval"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        pending = df[df['Approval Status'] == 'Pending']
        
        return {
            "pending_count": len(pending),
            "total_pending_value": float(pending['Grand Total'].sum()),
            "average_pending_value": float(pending['Grand Total'].mean()),
            "by_department": pending['Department'].value_counts().to_dict(),
            "by_assigned_to": pending['Assigned To'].value_counts().to_dict(),
            "orders": pending[['PO Number', 'Vendor', 'Grand Total', 'Department', 'Assigned To', 'Status']].to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders-by-date-range")
async def get_orders_by_date_range(start_date: str, end_date: str) -> Dict:
    """Get orders within a date range (YYYY-MM-DD format)"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        df['PO Date'] = pd.to_datetime(df['PO Date'], errors='coerce')
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        filtered = df[(df['PO Date'] >= start) & (df['PO Date'] <= end)]
        
        return {
            "date_range": f"{start_date} to {end_date}",
            "orders_count": len(filtered),
            "total_amount": float(filtered['Grand Total'].sum()),
            "average_amount": float(filtered['Grand Total'].mean()),
            "orders": filtered[['PO Number', 'PO Date', 'Vendor', 'Grand Total', 'Status']].to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/by-item-description")
async def get_by_item_description(item: Optional[str] = None) -> Dict:
    """Get orders by item description"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        if item:
            df = df[df['Item Description'].str.contains(item, case=False, na=False)]
        
        result = {}
        for desc in df['Item Description'].unique():
            desc_df = df[df['Item Description'] == desc]
            result[desc] = {
                "orders_count": len(desc_df),
                "total_value": float(desc_df['Grand Total'].sum()),
                "average_value": float(desc_df['Grand Total'].mean()),
                "vendors": desc_df['Vendor'].unique().tolist()
            }
        
        return {"by_item_description": result, "total_items": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_orders(
    query: str,
    search_fields: str = "all"
) -> Dict:
    """Search orders across multiple fields (all, vendor, po_number, item, notes)"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        query_lower = query.lower()
        
        if search_fields == "all":
            result = df[
                df.astype(str).apply(lambda x: x.str.contains(query_lower, case=False, na=False)).any(axis=1)
            ]
        elif search_fields == "vendor":
            result = df[df['Vendor'].str.contains(query, case=False, na=False)]
        elif search_fields == "po_number":
            result = df[df['PO Number'].str.contains(query, case=False, na=False)]
        elif search_fields == "item":
            result = df[df['Item Description'].str.contains(query, case=False, na=False)]
        elif search_fields == "notes":
            result = df[df['Notes'].str.contains(query, case=False, na=False)]
        else:
            result = df
        
        return {
            "query": query,
            "search_fields": search_fields,
            "results_count": len(result),
            "total_value": float(result['Grand Total'].sum()),
            "orders": result[['PO Number', 'Vendor', 'Item Description', 'Grand Total', 'Status']].to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary-dashboard")
async def get_summary_dashboard() -> Dict:
    """Get comprehensive dashboard summary with all key metrics"""
    try:
        check_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        
        return {
            "total_orders": len(df),
            "grand_total_all": float(df['Grand Total'].sum()),
            "average_order_value": float(df['Grand Total'].mean()),
            "min_order_value": float(df['Grand Total'].min()),
            "max_order_value": float(df['Grand Total'].max()),
            "by_status": df['Status'].value_counts().to_dict(),
            "by_approval_status": df['Approval Status'].value_counts().to_dict(),
            "by_department": df['Department'].value_counts().to_dict(),
            "by_location": df['Location'].value_counts().to_dict(),
            "by_vendor": df['Vendor'].value_counts().head(10).to_dict(),
            "by_currency": df['Currency'].value_counts().to_dict(),
            "by_payment_terms": df['Payment Terms'].value_counts().to_dict(),
            "total_tax_collected": float(df['Tax Amount'].sum()),
            "avg_tax_per_order": float(df['Tax Amount'].mean()),
            "pending_approvals_count": len(df[df['Approval Status'] == 'Pending']),
            "approved_orders_count": len(df[df['Approval Status'] == 'Approved'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
