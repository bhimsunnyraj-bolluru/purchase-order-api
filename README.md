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

### Statistics & Analytics
- `GET /api/statistics` - Get comprehensive statistics about all orders
  - Returns: total count, totals, averages, breakdowns by status, vendor, department, etc.

- `GET /api/vendors` - Get list of unique vendors

- `GET /api/departments` - Get list of unique departments

### Download
- `GET /api/download` - Download the entire CSV file

### Export
- `POST /api/export` - Export filtered data as JSON
  - Query params: `vendor`, `status`

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

# Get statistics
curl http://localhost:8000/api/statistics

# Get a specific order
curl http://localhost:8000/api/orders/PO-2026-12345

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
