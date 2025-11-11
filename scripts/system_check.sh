#!/bin/bash
###############################################################################
# LOKI Platform System Diagnostics
# Comprehensive system health and readiness checks
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    ((CHECKS_WARNING++))
}

print_info() {
    echo -e "    $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_header "LOKI PLATFORM SYSTEM DIAGNOSTICS"
echo "Project Root: $PROJECT_ROOT"
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo

# 1. Python Environment Check
print_header "1. PYTHON ENVIRONMENT"

print_check "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"

    # Check if version is 3.8+
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python version is compatible (>= 3.8)"
    else
        print_error "Python version must be 3.8 or higher"
    fi
else
    print_error "Python 3 not found"
fi

print_check "Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    print_success "pip found: $PIP_VERSION"
else
    print_error "pip3 not found"
fi

print_check "Checking virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    print_success "Virtual environment active: $VIRTUAL_ENV"
else
    print_warning "No virtual environment detected (recommended to use one)"
fi

# 2. Required Dependencies
print_header "2. REQUIRED DEPENDENCIES"

print_check "Checking Python packages..."
cd "$PROJECT_ROOT"

REQUIRED_PACKAGES=(
    "fastapi"
    "sqlalchemy"
    "redis"
    "psutil"
    "pyyaml"
    "click"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        print_success "$package installed (version: $VERSION)"
    else
        print_error "$package not installed"
    fi
done

# 3. Database Connectivity
print_header "3. DATABASE CONNECTIVITY"

print_check "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL client found"

    # Try to connect (will fail gracefully if not configured)
    if [ -n "$DB_HOST" ]; then
        print_info "Database host: ${DB_HOST:-localhost}"
        print_info "Database port: ${DB_PORT:-5432}"
        print_info "Database name: ${DB_NAME:-loki}"
    else
        print_warning "Database environment variables not set"
    fi
else
    print_warning "PostgreSQL client not found (optional if using remote DB)"
fi

# 4. Redis Connectivity
print_header "4. REDIS CONNECTIVITY"

print_check "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    print_success "Redis CLI found"

    # Try to ping Redis
    REDIS_HOST=${REDIS_HOST:-localhost}
    REDIS_PORT=${REDIS_PORT:-6379}

    if timeout 2 redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &> /dev/null; then
        print_success "Redis is responsive at $REDIS_HOST:$REDIS_PORT"
    else
        print_warning "Could not connect to Redis at $REDIS_HOST:$REDIS_PORT"
    fi
else
    print_warning "Redis CLI not found (optional if using remote Redis)"
fi

# 5. System Resources
print_header "5. SYSTEM RESOURCES"

print_check "Checking CPU..."
CPU_COUNT=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
print_info "CPU cores: $CPU_COUNT"

if [ "$CPU_COUNT" != "unknown" ] && [ "$CPU_COUNT" -ge 2 ]; then
    print_success "Sufficient CPU cores (>= 2)"
else
    print_warning "Limited CPU cores detected"
fi

print_check "Checking memory..."
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -m | awk 'NR==2 {print $2}')
    AVAILABLE_MEM=$(free -m | awk 'NR==2 {print $7}')
    print_info "Total memory: ${TOTAL_MEM}MB"
    print_info "Available memory: ${AVAILABLE_MEM}MB"

    if [ "$TOTAL_MEM" -ge 2048 ]; then
        print_success "Sufficient memory (>= 2GB)"
    else
        print_warning "Limited memory (recommended: >= 2GB)"
    fi
elif command -v vm_stat &> /dev/null; then
    # macOS
    print_info "Memory check (macOS detected)"
    print_success "Memory information available via vm_stat"
else
    print_warning "Could not determine memory information"
fi

print_check "Checking disk space..."
DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
DISK_AVAIL=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')

print_info "Disk usage: ${DISK_USAGE}%"
print_info "Available space: $DISK_AVAIL"

if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Sufficient disk space (< 80% used)"
elif [ "$DISK_USAGE" -lt 90 ]; then
    print_warning "Disk space is getting low (${DISK_USAGE}% used)"
else
    print_error "Critical disk space (${DISK_USAGE}% used)"
fi

# 6. File System Structure
print_header "6. FILE SYSTEM STRUCTURE"

REQUIRED_DIRS=(
    "backend"
    "backend/core"
    "backend/platform"
    "backend/modules"
    "frontend"
    "cli"
    "scripts"
    "tests"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        print_success "Directory exists: $dir"
    else
        print_error "Missing directory: $dir"
    fi
done

# 7. Configuration Files
print_header "7. CONFIGURATION FILES"

print_check "Checking configuration files..."

if [ -f "$PROJECT_ROOT/.env" ]; then
    print_success ".env file exists"
else
    print_warning ".env file not found (using environment variables)"
fi

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    print_success "requirements.txt exists"
    REQ_COUNT=$(wc -l < "$PROJECT_ROOT/requirements.txt")
    print_info "Dependencies listed: $REQ_COUNT"
else
    print_error "requirements.txt not found"
fi

# 8. Platform Components
print_header "8. PLATFORM COMPONENTS"

print_check "Checking platform modules..."

PLATFORM_MODULES=(
    "backend/platform/__init__.py"
    "backend/platform/orchestrator.py"
    "backend/platform/health_monitor.py"
    "backend/platform/feature_flags.py"
    "backend/platform/config.py"
    "backend/platform/telemetry.py"
    "backend/platform/error_handler.py"
)

for module in "${PLATFORM_MODULES[@]}"; do
    if [ -f "$PROJECT_ROOT/$module" ]; then
        print_success "Module exists: $module"
    else
        print_error "Missing module: $module"
    fi
done

# 9. Compliance Modules
print_header "9. COMPLIANCE MODULES"

print_check "Checking compliance modules..."

COMPLIANCE_MODULES=(
    "backend/modules/fca_uk"
    "backend/modules/fca_advanced"
    "backend/modules/gdpr_uk"
    "backend/modules/gdpr_advanced"
    "backend/modules/tax_uk"
    "backend/modules/uk_employment"
)

for module in "${COMPLIANCE_MODULES[@]}"; do
    if [ -d "$PROJECT_ROOT/$module" ]; then
        MODULE_NAME=$(basename "$module")
        GATE_COUNT=$(find "$PROJECT_ROOT/$module/gates" -name "*.py" ! -name "__init__.py" 2>/dev/null | wc -l)
        print_success "$MODULE_NAME found ($GATE_COUNT gates)"
    else
        print_warning "Module not found: $module"
    fi
done

# 10. Security Check
print_header "10. SECURITY CHECK"

print_check "Checking for sensitive files in git..."
if [ -d "$PROJECT_ROOT/.git" ]; then
    # Check if .env is in .gitignore
    if grep -q "^\.env$" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
        print_success ".env is in .gitignore"
    else
        print_warning ".env should be in .gitignore"
    fi

    # Check if .env is tracked
    if git -C "$PROJECT_ROOT" ls-files --error-unmatch .env &>/dev/null; then
        print_error ".env file is tracked by git (SECURITY RISK)"
    else
        print_success ".env file is not tracked by git"
    fi
else
    print_warning "Not a git repository"
fi

print_check "Checking environment variables..."
CRITICAL_ENV_VARS=(
    "DB_PASSWORD"
    "JWT_SECRET"
)

for var in "${CRITICAL_ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        print_success "$var is set"
    else
        print_warning "$var is not set (required for production)"
    fi
done

# 11. Port Availability
print_header "11. PORT AVAILABILITY"

print_check "Checking if required ports are available..."

PORTS=(
    "8000:API Server"
    "5432:PostgreSQL"
    "6379:Redis"
)

for port_info in "${PORTS[@]}"; do
    PORT=$(echo "$port_info" | cut -d: -f1)
    SERVICE=$(echo "$port_info" | cut -d: -f2)

    if command -v lsof &> /dev/null; then
        if lsof -Pi ":$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $PORT ($SERVICE) is already in use"
        else
            print_success "Port $PORT ($SERVICE) is available"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$PORT "; then
            print_warning "Port $PORT ($SERVICE) is already in use"
        else
            print_success "Port $PORT ($SERVICE) is available"
        fi
    else
        print_warning "Cannot check port availability (lsof/netstat not found)"
        break
    fi
done

# 12. Tests
print_header "12. TESTS"

print_check "Checking test infrastructure..."

if [ -d "$PROJECT_ROOT/tests" ]; then
    TEST_COUNT=$(find "$PROJECT_ROOT/tests" -name "test_*.py" | wc -l)
    print_success "Test directory exists ($TEST_COUNT test files)"
else
    print_warning "Tests directory not found"
fi

if [ -f "$PROJECT_ROOT/pytest.ini" ]; then
    print_success "pytest.ini exists"
else
    print_warning "pytest.ini not found"
fi

# Summary
print_header "SUMMARY"

TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))

echo -e "${GREEN}Passed:${NC}   $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "${RED}Failed:${NC}   $CHECKS_FAILED"
echo -e "Total:    $TOTAL_CHECKS"
echo

if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo -e "${GREEN}✓ System is ready for deployment!${NC}\n"
        exit 0
    else
        echo -e "${YELLOW}⚠ System is operational but has warnings${NC}\n"
        exit 0
    fi
else
    echo -e "${RED}✗ System has critical issues that must be resolved${NC}\n"
    exit 1
fi
