#!/bin/bash
#
# Correction Testing Suite Runner
#
# Runs comprehensive tests for the correction system with various options
# for coverage, performance benchmarking, and reporting.
#
# Usage:
#   ./scripts/run_correction_tests.sh [options]
#
# Options:
#   --all              Run all tests (default)
#   --accuracy         Run accuracy tests only
#   --regression       Run regression tests only
#   --property         Run property-based tests only
#   --performance      Run performance benchmarks only
#   --adversarial      Run adversarial tests only
#   --coverage         Generate coverage report
#   --html             Generate HTML coverage report
#   --benchmark        Run with benchmark output
#   --markers MARKERS  Run tests with specific markers
#   --verbose          Verbose output
#   --quiet            Minimal output
#   --parallel         Run tests in parallel (faster)
#   --report           Generate comprehensive test report
#   --help             Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TESTS_DIR="tests/correction"
COVERAGE=false
HTML_COVERAGE=false
BENCHMARK=false
VERBOSE=false
QUIET=false
PARALLEL=false
REPORT=false
TEST_SUITE="all"
MARKERS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            TEST_SUITE="all"
            shift
            ;;
        --accuracy)
            TEST_SUITE="accuracy"
            shift
            ;;
        --regression)
            TEST_SUITE="regression"
            shift
            ;;
        --property)
            TEST_SUITE="property"
            shift
            ;;
        --performance)
            TEST_SUITE="performance"
            shift
            ;;
        --adversarial)
            TEST_SUITE="adversarial"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --html)
            HTML_COVERAGE=true
            COVERAGE=true
            shift
            ;;
        --benchmark)
            BENCHMARK=true
            shift
            ;;
        --markers)
            MARKERS="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --report)
            REPORT=true
            shift
            ;;
        --help)
            grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     LOKI Correction System - Test Suite Runner            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install -r requirements-test.txt"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest"

# Add test path based on suite
case $TEST_SUITE in
    all)
        echo -e "${GREEN}Running all correction tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR"
        ;;
    accuracy)
        echo -e "${GREEN}Running accuracy tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/test_accuracy.py"
        ;;
    regression)
        echo -e "${GREEN}Running regression tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/test_regression.py"
        ;;
    property)
        echo -e "${GREEN}Running property-based tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/test_property_based.py"
        ;;
    performance)
        echo -e "${GREEN}Running performance benchmarks...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/test_performance.py"
        BENCHMARK=true  # Auto-enable benchmark for performance tests
        ;;
    adversarial)
        echo -e "${GREEN}Running adversarial tests...${NC}"
        PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/adversarial/"
        ;;
esac

# Add verbosity options
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
elif [ "$QUIET" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -q"
else
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage options
if [ "$COVERAGE" = true ]; then
    echo -e "${YELLOW}Coverage reporting enabled${NC}"
    PYTEST_CMD="$PYTEST_CMD --cov=backend/core --cov=backend/testing"
    PYTEST_CMD="$PYTEST_CMD --cov-report=term-missing"

    if [ "$HTML_COVERAGE" = true ]; then
        echo -e "${YELLOW}HTML coverage report will be generated${NC}"
        PYTEST_CMD="$PYTEST_CMD --cov-report=html:htmlcov/correction"
    fi
fi

# Add benchmark options
if [ "$BENCHMARK" = true ]; then
    echo -e "${YELLOW}Benchmark mode enabled${NC}"
    PYTEST_CMD="$PYTEST_CMD --benchmark-only"
    PYTEST_CMD="$PYTEST_CMD --benchmark-autosave"
    PYTEST_CMD="$PYTEST_CMD --benchmark-compare"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    echo -e "${YELLOW}Parallel execution enabled${NC}"
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add markers
if [ -n "$MARKERS" ]; then
    echo -e "${YELLOW}Running tests with markers: $MARKERS${NC}"
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKERS\""
fi

# Add report generation
if [ "$REPORT" = true ]; then
    echo -e "${YELLOW}Test report will be generated${NC}"
    PYTEST_CMD="$PYTEST_CMD --html=reports/correction_tests.html --self-contained-html"
    PYTEST_CMD="$PYTEST_CMD --json-report --json-report-file=reports/correction_tests.json"

    # Create reports directory if it doesn't exist
    mkdir -p reports
fi

echo ""
echo -e "${BLUE}Command: $PYTEST_CMD${NC}"
echo ""

# Run tests
START_TIME=$(date +%s)

if eval $PYTEST_CMD; then
    EXIT_CODE=0
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    EXIT_CODE=$?
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}Test execution completed in ${DURATION}s${NC}"

# Post-test actions
if [ "$HTML_COVERAGE" = true ] && [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/correction/index.html${NC}"
fi

if [ "$REPORT" = true ] && [ -f "reports/correction_tests.html" ]; then
    echo -e "${GREEN}Test report generated: reports/correction_tests.html${NC}"
fi

# Print summary recommendations
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                     Tests Successful                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "  - Review coverage report for gaps"
        echo "  - Add tests for uncovered code paths"
        echo "  - Consider adding edge cases"
    fi
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                     Tests Failed                           ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  - Review failed test output above"
    echo "  - Run with --verbose for more details"
    echo "  - Check test_*.py files for assertions"
    echo "  - Verify correction patterns are correct"
fi

echo ""

exit $EXIT_CODE
