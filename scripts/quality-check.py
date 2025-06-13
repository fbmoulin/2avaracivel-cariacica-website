#!/usr/bin/env python3
"""
Quality assurance automation script for 2ª Vara Cível de Cariacica
Runs comprehensive code quality checks, security audits, and performance tests
"""

import subprocess
import sys
import json
from datetime import datetime


def run_command_with_output(command, description=""):
    """Run command and return both success status and output"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}: PASSED")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}: FAILED")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False, e.stdout


def run_code_formatting():
    """Run code formatting checks"""
    print("\n🎨 Code Formatting Checks")
    print("-" * 30)
    
    results = []
    
    # Black formatting check
    success, output = run_command_with_output(
        "poetry run black --check --diff .",
        "Black code formatting"
    )
    results.append(("Black formatting", success))
    
    # isort import sorting check
    success, output = run_command_with_output(
        "poetry run isort --check-only --diff .",
        "Import sorting (isort)"
    )
    results.append(("Import sorting", success))
    
    return results


def run_linting():
    """Run code linting checks"""
    print("\n🔍 Code Linting")
    print("-" * 30)
    
    results = []
    
    # Flake8 linting
    success, output = run_command_with_output(
        "poetry run flake8 .",
        "Flake8 linting"
    )
    results.append(("Flake8 linting", success))
    
    # MyPy type checking
    success, output = run_command_with_output(
        "poetry run mypy .",
        "Type checking (MyPy)"
    )
    results.append(("Type checking", success))
    
    return results


def run_security_audit():
    """Run security audit checks"""
    print("\n🛡️ Security Audit")
    print("-" * 30)
    
    results = []
    
    # Bandit security linting
    success, output = run_command_with_output(
        "poetry run bandit -r . -f json",
        "Security audit (Bandit)"
    )
    results.append(("Security audit", success))
    
    # Safety dependency vulnerability check
    success, output = run_command_with_output(
        "poetry run safety check",
        "Dependency vulnerability check"
    )
    results.append(("Dependency security", success))
    
    return results


def run_tests():
    """Run comprehensive test suite"""
    print("\n🧪 Test Suite")
    print("-" * 30)
    
    results = []
    
    # Unit tests
    success, output = run_command_with_output(
        "poetry run pytest tests/unit/ -v --tb=short",
        "Unit tests"
    )
    results.append(("Unit tests", success))
    
    # Integration tests
    success, output = run_command_with_output(
        "poetry run pytest tests/integration/ -v --tb=short",
        "Integration tests"
    )
    results.append(("Integration tests", success))
    
    # Security tests
    success, output = run_command_with_output(
        "poetry run pytest tests/security/ -v --tb=short",
        "Security tests"
    )
    results.append(("Security tests", success))
    
    # Test coverage
    success, output = run_command_with_output(
        "poetry run pytest --cov=. --cov-report=term-missing",
        "Test coverage analysis"
    )
    results.append(("Test coverage", success))
    
    return results


def run_accessibility_check():
    """Run accessibility compliance checks"""
    print("\n♿ Accessibility Compliance")
    print("-" * 30)
    
    results = []
    
    # Accessibility tests
    success, output = run_command_with_output(
        "poetry run pytest tests/accessibility/ -v",
        "WCAG 2.1 AA compliance tests"
    )
    results.append(("Accessibility tests", success))
    
    return results


def generate_quality_report(all_results):
    """Generate comprehensive quality report"""
    print("\n📊 Quality Assessment Report")
    print("=" * 50)
    
    total_checks = sum(len(category_results) for category_results in all_results.values())
    passed_checks = sum(
        sum(1 for _, success in category_results if success) 
        for category_results in all_results.values()
    )
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Overall Quality Score: {success_rate:.1f}%")
    print(f"Checks Passed: {passed_checks}/{total_checks}")
    print()
    
    for category, results in all_results.items():
        category_passed = sum(1 for _, success in results if success)
        category_total = len(results)
        category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        
        status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 80 else "❌"
        print(f"{status} {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
        
        for check_name, success in results:
            check_status = "✅" if success else "❌"
            print(f"    {check_status} {check_name}")
    
    print()
    
    if success_rate >= 95:
        print("🟢 EXCELLENT: Code quality meets production standards")
    elif success_rate >= 85:
        print("🟡 GOOD: Minor issues detected, mostly ready for production")
    elif success_rate >= 70:
        print("🟠 FAIR: Several issues need attention before production")
    else:
        print("🔴 POOR: Significant quality issues must be resolved")
    
    return success_rate


def main():
    """Main quality check function"""
    print("🏛️ 2ª Vara Cível de Cariacica - Quality Assurance Check")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {}
    
    # Run all quality checks
    all_results["Code Formatting"] = run_code_formatting()
    all_results["Code Linting"] = run_linting()
    all_results["Security Audit"] = run_security_audit()
    all_results["Test Suite"] = run_tests()
    all_results["Accessibility"] = run_accessibility_check()
    
    # Generate comprehensive report
    success_rate = generate_quality_report(all_results)
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 85 else 1)


if __name__ == "__main__":
    main()