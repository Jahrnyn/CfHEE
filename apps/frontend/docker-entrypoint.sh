#!/bin/sh
set -eu

API_BASE_URL="${CFHEE_API_BASE_URL:-http://127.0.0.1:8000}"

cat > /usr/share/nginx/html/runtime-config.js <<EOF
window.__CFHEE_RUNTIME_CONFIG__ = {
  apiBaseUrl: "${API_BASE_URL}"
};
EOF

exec nginx -g 'daemon off;'
