#!/usr/bin/env bash
# Self-test script for Sonoma investigation environment
set -euo pipefail

echo "🔍 Sonoma Investigation Self-Test"
echo "================================"

# Check for required environment variables
check_env() {
    local var=$1
    if [[ -z "${!var:-}" ]]; then
        echo "❌ Missing required environment variable: $var"
        return 1
    else
        echo "✓ $var is set"
        return 0
    fi
}

# Test environment
echo -e "\n1. Environment Variables:"
all_good=true
check_env "GROK_API_KEY" || all_good=false
check_env "X_CLIENT_TRACE" || all_good=false
check_env "ENDPOINT" || all_good=false
check_env "MODEL" || all_good=false
check_env "INTENT" || all_good=false

if ! $all_good; then
    echo -e "\n⚠️  Please source your .env file first:"
    echo "   set -a; source $HOME/sonoma_investigation/.env; set +a"
    exit 1
fi

# Test Python secrets module
echo -e "\n2. Python Secrets Module:"
python3 -c "
import sys
sys.path.insert(0, '$HOME/sonoma_investigation')
try:
    import secrets
    key = secrets.get_api_key()
    print('✓ secrets.py loads correctly')
    print(f'✓ API key starts with: {key[:8]}...')
except Exception as e:
    print(f'❌ Error loading secrets: {e}')
    sys.exit(1)
"

# Check directory structure
echo -e "\n3. Directory Structure:"
for dir in raw catalog embeddings scripts; do
    if [[ -d "$HOME/sonoma_investigation/$dir" ]]; then
        echo "✓ $dir/ exists"
    else
        echo "❌ Missing directory: $dir/"
    fi
done

# Check for required files
echo -e "\n4. Required Files:"
for file in config.yml .gitignore secrets.py; do
    if [[ -f "$HOME/sonoma_investigation/$file" ]]; then
        echo "✓ $file exists"
    else
        echo "❌ Missing file: $file"
    fi
done

# Verify config integrity
echo -e "\n5. Config Integrity:"
cd "$HOME/sonoma_investigation"
if shasum -a 256 -c config.yml.sha256 >/dev/null 2>&1; then
    echo "✓ config.yml integrity verified"
else
    echo "⚠️  config.yml may have been modified"
fi

# Test API connectivity (dry run)
echo -e "\n6. API Endpoint Test (dry run):"
if curl -s --max-time 5 -o /dev/null -w "%{http_code}" "$ENDPOINT" | grep -q "40[0-9]"; then
    echo "✓ API endpoint is reachable (got expected 40x without auth)"
else
    echo "⚠️  Could not reach API endpoint"
fi

echo -e "\n✅ Self-test complete!"
