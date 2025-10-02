#!/bin/bash
# Test AI Analysis Features

echo "=== Testing AI Analysis with Gemini 2.0 Flash Experimental ==="
echo ""

# Test 1: Check provider
echo "1. Testing provider detection..."
curl -s "http://localhost:5000/api/stock/AAPL/analyze-with-ai" | python3 -c "import sys, json; data = json.load(sys.stdin); print('Provider:', data.get('provider')); print('Confidence:', data.get('confidence_score'))"
echo ""

# Test 2: Check all sections are present
echo "2. Testing section completeness..."
curl -s "http://localhost:5000/api/stock/MSFT/analyze-with-ai" | python3 -c "
import sys, json
data = json.load(sys.stdin)
ai = data['ai_analysis']
sections = ['technical_analysis', 'fundamental_analysis', 'risks', 'opportunities', 'price_target', 'short_squeeze', 'recommendation']
for section in sections:
    length = len(ai.get(section, ''))
    status = '✅' if length > 50 else '❌'
    print(f'{status} {section}: {length} chars')
"
echo ""

# Test 3: Check for specific data in Short Squeeze
echo "3. Testing Short Squeeze Due Diligence..."
curl -s "http://localhost:5000/api/stock/GME/analyze-with-ai" | python3 -c "
import sys, json
data = json.load(sys.stdin)
squeeze = data['ai_analysis'].get('short_squeeze', '')
print('Short Squeeze section length:', len(squeeze))
print('Contains Freefloat:', '✅' if 'freefloat' in squeeze.lower() else '❌')
print('Contains Short Interest:', '✅' if 'short interest' in squeeze.lower() else '❌')
print('Contains Days to Cover:', '✅' if 'days to cover' in squeeze.lower() else '❌')
print('Contains FTD:', '✅' if 'ftd' in squeeze.lower() or 'failure to deliver' in squeeze.lower() else '❌')
print('Contains Probability:', '✅' if 'wahrscheinlich' in squeeze.lower() or 'probability' in squeeze.lower() else '❌')
"
echo ""

echo "=== Test Complete ==="
