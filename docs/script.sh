#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${DOCS_DIR}/_build/html"

echo "Building documentation..."
sphinx-build -b html "${DOCS_DIR}" "${BUILD_DIR}"
echo "Documentation built at ${BUILD_DIR}/index.html"
