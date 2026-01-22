const fs = require('fs');
const path = require('path');

// Sample data for generating realistic PO data
const vendors = [
  'Acme Corp',
  'Global Supplies Inc',
  'Tech Solutions Ltd',
  'Premium Materials Co',
  'Industrial Parts Group',
  'Office Plus',
  'Digital Systems',
  'Component World',
  'Quality Distributors',
  'Enterprise Solutions'
];

const items = [
  'Laptop',
  'Monitor',
  'Keyboard',
  'Mouse',
  'USB Cable',
  'Desk Chair',
  'Office Desk',
  'Filing Cabinet',
  'Printer Paper',
  'Ink Cartridge',
  'Server RAM',
  'SSD Storage',
  'Network Switch',
  'Router',
  'Power Supply'
];

const statuses = ['Draft', 'Pending', 'Approved', 'Received', 'Cancelled', 'Partial'];
const priorities = ['Low', 'Medium', 'High', 'Urgent'];
const paymentTerms = ['Net 30', 'Net 60', 'Net 90', 'COD', '2/10 Net 30', 'Due on Receipt'];
const currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD'];

// Helper functions
function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function generatePONumber() {
  const year = new Date().getFullYear();
  const random = String(randomBetween(10000, 99999));
  return `PO-${year}-${random}`;
}

function generateDate(daysOffset = 0) {
  const date = new Date();
  date.setDate(date.getDate() + daysOffset);
  return date.toISOString().split('T')[0];
}

function generateRandomItem() {
  const quantity = randomBetween(1, 100);
  const unitPrice = (Math.random() * 1000).toFixed(2);
  const totalPrice = (quantity * unitPrice).toFixed(2);
  
  return {
    itemName: getRandomElement(items),
    quantity,
    unitPrice,
    totalPrice,
    category: getRandomElement(['Electronics', 'Furniture', 'Supplies', 'Hardware'])
  };
}

function generatePORecord() {
  const poDate = generateDate();
  const deliveryDate = generateDate(randomBetween(5, 30));
  const numItems = randomBetween(1, 5);
  let lineItems = [];
  let totalAmount = 0;
  
  for (let i = 0; i < numItems; i++) {
    const item = generateRandomItem();
    lineItems.push(item);
    totalAmount += parseFloat(item.totalPrice);
  }
  
  const itemsDescription = lineItems.map(item => `${item.quantity}x ${item.itemName}`).join('; ');
  const itemsTotal = lineItems.map(item => item.totalPrice).reduce((a, b) => a + parseFloat(b), 0);
  
  return {
    'PO Number': generatePONumber(),
    'Vendor': getRandomElement(vendors),
    'PO Date': poDate,
    'Delivery Date': deliveryDate,
    'Expected Delivery': deliveryDate,
    'Item Description': itemsDescription,
    'Quantity': lineItems.reduce((sum, item) => sum + item.quantity, 0),
    'Unit Price': lineItems[0].unitPrice,
    'Total Amount': itemsTotal.toFixed(2),
    'Currency': getRandomElement(currencies),
    'Payment Terms': getRandomElement(paymentTerms),
    'Department': getRandomElement(['IT', 'Operations', 'Finance', 'HR', 'Logistics']),
    'Location': getRandomElement(['New York', 'Los Angeles', 'Chicago', 'Toronto', 'London', 'Sydney']),
    'Approval Status': getRandomElement(['Pending', 'Approved', 'Rejected']),
    'Priority': getRandomElement(priorities),
    'Notes': getRandomElement(['', 'Urgent delivery required', 'Special packaging needed', 'Standard delivery', 'Quality inspection required']),
    'Tax Amount': (itemsTotal * 0.1).toFixed(2),
    'Grand Total': (itemsTotal * 1.1).toFixed(2),
    'Created By': getRandomElement(['John Smith', 'Sarah Johnson', 'Mike Davis', 'Emily Chen', 'Robert Wilson']),
    'Assigned To': getRandomElement(['Alice Brown', 'David Lee', 'Lisa Anderson', 'Tom Martinez', 'Jessica White'])
  };
}

function generateCSV(recordCount = 10000) {
  // Generate records
  const records = [];
  for (let i = 0; i < recordCount; i++) {
    records.push(generatePORecord());
  }
  
  // Get headers from first record
  const headers = Object.keys(records[0]);
  
  // Create CSV content
  let csv = headers.join(',') + '\n';
  
  records.forEach(record => {
    const values = headers.map(header => {
      let value = record[header];
      // Escape values containing commas, quotes, or newlines
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        value = '"' + value.replace(/"/g, '""') + '"';
      }
      return value;
    });
    csv += values.join(',') + '\n';
  });
  
  return csv;
}

// Main execution
const args = process.argv.slice(2);
const recordCount = args[0] ? parseInt(args[0]) : 10000;

console.log(`Generating ${recordCount} Purchase Order records...`);

const csvData = generateCSV(recordCount);
const outputFile = path.join(__dirname, 'purchase_orders.csv');

fs.writeFileSync(outputFile, csvData, 'utf8');
console.log(`✓ CSV file created successfully: ${outputFile}`);
console.log(`✓ Total records: ${recordCount}`);
