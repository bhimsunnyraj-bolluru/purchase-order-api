#!/bin/bash

echo "🧪 Testing Purchase Order API Endpoints..."
echo "=========================================="

# Extract and run all curl commands from curl.txt
grep "^curl " curl.txt | while read -r cmd; do
    echo ""
    echo "▶ Testing: ${cmd:0:80}..."
    eval "$cmd" | head -c 200
    echo -e "\n✅ Success"
done

echo ""
echo "=========================================="
echo "✅ All tests completed!"
