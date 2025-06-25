#!/usr/bin/env python3
"""
Test runner for Italian Medical NER project
Provides easy way to run different test categories
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def run_tests(test_type="all", verbose=False):
    """
    Run tests with specified parameters
    
    Args:
        test_type: Type of tests to run (all, unit, integration, api, mock, slow)
        verbose: Whether to run in verbose mode
    """
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if verbose:
        pytest_cmd.append("-v")
    
    # Add test type markers
    if test_type != "all":
        pytest_cmd.extend(["-m", test_type])
    
    # Add test directory
    pytest_cmd.append("tests/")
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(pytest_cmd)}")
    print("-" * 60)
    
    # Run the tests
    returncode, stdout, stderr = run_command(" ".join(pytest_cmd))
    
    # Print results
    if stdout:
        print(stdout)
    if stderr:
        print("STDERR:", stderr)
    
    return returncode == 0

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["pytest", "torch", "transformers"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Italian Medical NER tests")
    parser.add_argument(
        "--type", "-t", 
        choices=["all", "unit", "integration", "api", "mock", "slow"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--check-deps", "-c",
        action="store_true", 
        help="Check dependencies only"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage report"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check_deps:
        if check_dependencies():
            print("✅ All dependencies are installed")
            return 0
        else:
            return 1
    
    if not check_dependencies():
        print("❌ Missing dependencies. Use --check-deps to see details.")
        return 1
    
    # Run tests with coverage if requested
    if args.coverage:
        try:
            import coverage
            print("Running tests with coverage...")
            cmd = f"python -m coverage run -m pytest tests/ && python -m coverage report"
            returncode, stdout, stderr = run_command(cmd)
            if stdout:
                print(stdout)
            if stderr:
                print("STDERR:", stderr)
            return 0 if returncode == 0 else 1
        except ImportError:
            print("Coverage package not installed. Install with: pip install coverage")
            return 1
    
    # Run the tests
    success = run_tests(args.type, args.verbose)
    
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
