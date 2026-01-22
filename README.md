# Purchase Order FastAPI Project

A FastAPI application to read, filter, and manage Purchase Order data from CSV files.

## Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Generate CSV data (if not already done):**
```bash
node generatePOData.js 50
```

3. **Run the API server:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Root Endpoint
- `GET /` - Welcome message with available endpoints

### Purchase Order Endpoints
- `GET /api/orders` - Get all orders with pagination and filtering
  - Query params: `skip`, `limit`, `vendor`, `status`
  - Example: `/api/orders?vendor=Acme&status=Approved&skip=0&limit=10`

- `GET /api/orders/{po_number}` - Get a specific order by PO Number
  - Example: `/api/orders/PO-2026-12345`

### Approval & Assignment Endpoints
- `GET /api/approval-summary` - Get approval status breakdown with assigned personnel and grand totals
  
- `GET /api/assigned-to` - Get orders grouped by assigned person with grand totals
  - Query params: `assigned_to` (optional)
  - Example: `/api/assigned-to?assigned_to=Alice`

- `GET /api/pending-approvals` - Get all orders pending approval with department & assignment breakdown

### Department & Location Endpoints
- `GET /api/by-department` - Get orders grouped by department with financial metrics
  - Query params: `department` (optional)
  - Example: `/api/by-department?department=IT`

- `GET /api/by-location` - Get orders grouped by location with department info
  - Query params: `location` (optional)
  - Example: `/api/by-location?location=New%20York`

### Financial & Payment Endpoints
- `GET /api/by-currency` - Get orders grouped by currency with min/max/average amounts
  - Query params: `currency` (optional)
  - Example: `/api/by-currency?currency=USD`

- `GET /api/by-payment-terms` - Get orders grouped by payment terms
  - Query params: `payment_terms` (optional)
  - Example: `/api/by-payment-terms?payment_terms=Net%2030`

- `GET /api/high-value-orders` - Get orders above minimum amount
  - Query params: `min_amount` (default: 5000)
  - Example: `/api/high-value-orders?min_amount=10000`

### User & Item Endpoints
- `GET /api/by-created-by` - Get orders created by specific person with approval breakdown
  - Query params: `created_by` (optional)
  - Example: `/api/by-created-by?created_by=John`

- `GET /api/by-item-description` - Get orders by item type
  - Query params: `item` (optional)
  - Example: `/api/by-item-description?item=Laptop`

### Date & Search Endpoints
- `GET /api/orders-by-date-range` - Get orders within a date range (YYYY-MM-DD format)
  - Query params: `start_date`, `end_date` (required)
  - Example: `/api/orders-by-date-range?start_date=2026-01-01&end_date=2026-01-31`

- `GET /api/search` - Full-text search across all fields
  - Query params: `query` (required), `search_fields` (all/vendor/po_number/item/notes)
  - Example: `/api/search?query=Acme&search_fields=vendor`

### Statistics & Analytics
- `GET /api/statistics` - Get comprehensive statistics about all orders
  - Returns: total count, totals, averages, breakdowns by status, vendor, department, etc.

- `GET /api/summary-dashboard` - Get complete dashboard with all key metrics
  - Returns: order counts, totals, breakdowns by all dimensions, pending approvals count

- `GET /api/vendors` - Get list of unique vendors

- `GET /api/departments` - Get list of unique departments

### Download & Export
- `GET /api/download` - Download the entire CSV file

- `POST /api/export` - Export filtered data as JSON
  - Query params: `vendor`, `status` (optional)

## Interactive API Documentation

After starting the server, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Example Usage

```bash
# Get all orders
curl http://localhost:8000/api/orders

# Get orders from a specific vendor
curl http://localhost:8000/api/orders?vendor=Acme

# Get orders with specific status
curl http://localhost:8000/api/orders?status=Approved

# Get a specific order by PO number
curl http://localhost:8000/api/orders/PO-2026-12345

# Get approval status summary
curl http://localhost:8000/api/approval-summary

# Get orders assigned to a specific person
curl http://localhost:8000/api/assigned-to?assigned_to=Alice

# Get orders by department
curl http://localhost:8000/api/by-department?department=IT

# Get orders by location
curl http://localhost:8000/api/by-location?location=New%20York

# Get high-value orders (over $10,000)
curl http://localhost:8000/api/high-value-orders?min_amount=10000

# Get pending approvals
curl http://localhost:8000/api/pending-approvals

# Get orders within date range
curl http://localhost:8000/api/orders-by-date-range?start_date=2026-01-01&end_date=2026-01-31

# Search for orders
curl http://localhost:8000/api/search?query=Acme&search_fields=vendor

# Get complete dashboard
curl http://localhost:8000/api/summary-dashboard

# Get statistics
curl http://localhost:8000/api/statistics

# Download CSV
curl http://localhost:8000/api/download -o export.csv
```

## Project Structure

```
PO/
├── generatePOData.js       # Node.js script to generate CSV data
├── purchase_orders.csv     # Generated CSV file
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Notes

- The API reads from `purchase_orders.csv` in the same directory
- Make sure to run `generatePOData.js` first to create the CSV file
- Default pagination limit is 100 records (max 1000)
- All string searches are case-insensitive
