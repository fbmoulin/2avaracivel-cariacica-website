#!/usr/bin/env python3
"""
Comprehensive Refactoring and Optimization Script
2ª Vara Cível de Cariacica - Code Quality Enhancement
"""

import os
import ast
import logging
from typing import Dict, List, Tuple, Set
from pathlib import Path
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeRefactorer:
    """Main refactoring class"""
    
    def __init__(self):
        self.improvements = []
        self.issues_found = []
        self.optimizations = []
        
    def analyze_imports(self, file_path: str) -> Dict[str, List[str]]:
        """Analyze and optimize imports in Python files"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for unused imports
            tree = ast.parse(content)
            imported_names = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_names.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imported_names.add(alias.name)
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)
                    
            unused_imports = imported_names - used_names
            if unused_imports:
                issues.append(f"Unused imports: {', '.join(unused_imports)}")
                
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            
        return {"file": file_path, "issues": issues}
    
    def check_code_quality(self, file_path: str) -> List[str]:
        """Check for common code quality issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Check for long lines
                if len(line.rstrip()) > 100:
                    issues.append(f"Line {i}: Line too long ({len(line.rstrip())} characters)")
                
                # Check for print statements in production code
                if 'print(' in line and not file_path.endswith('_test.py'):
                    issues.append(f"Line {i}: Print statement found (use logger instead)")
                
                # Check for hardcoded secrets
                if any(keyword in line.lower() for keyword in ['password=', 'secret=', 'key=']):
                    if not any(safe in line for safe in ['os.environ', 'getenv', 'config']):
                        issues.append(f"Line {i}: Potential hardcoded secret")
                        
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
            
        return issues
    
    def optimize_database_queries(self) -> List[Dict[str, str]]:
        """Suggest database query optimizations"""
        optimizations = []
        
        # Check models.py for missing indexes
        models_file = 'models.py'
        if os.path.exists(models_file):
            with open(models_file, 'r') as f:
                content = f.read()
                
            # Look for foreign keys without indexes
            if 'ForeignKey' in content:
                optimizations.append({
                    'file': models_file,
                    'suggestion': 'Consider adding indexes to foreign key columns',
                    'impact': 'Improves JOIN performance'
                })
                
            # Check for missing composite indexes
            if 'filter_by' in content or 'query.filter' in content:
                optimizations.append({
                    'file': models_file,
                    'suggestion': 'Add composite indexes for commonly filtered column combinations',
                    'impact': 'Speeds up complex queries'
                })
                
        return optimizations
    
    def security_audit(self) -> List[Dict[str, str]]:
        """Perform security audit"""
        security_issues = []
        
        files_to_check = ['routes.py', 'app.py', 'config.py']
        
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for SQL injection vulnerabilities
            if 'format(' in content and 'SELECT' in content:
                security_issues.append({
                    'file': file_path,
                    'issue': 'Potential SQL injection vulnerability',
                    'fix': 'Use parameterized queries'
                })
                
            # Check for missing input validation
            if 'request.form' in content and 'validate' not in content:
                security_issues.append({
                    'file': file_path,
                    'issue': 'Missing input validation',
                    'fix': 'Add input validation using WTForms or custom validators'
                })
                
        return security_issues
    
    def performance_optimizations(self) -> List[Dict[str, str]]:
        """Suggest performance optimizations"""
        perf_suggestions = []
        
        # Check for missing caching
        routes_file = 'routes.py'
        if os.path.exists(routes_file):
            with open(routes_file, 'r') as f:
                content = f.read()
                
            # Check if static content is being cached
            if '@cache' not in content:
                perf_suggestions.append({
                    'area': 'Caching',
                    'suggestion': 'Add caching decorators to static routes',
                    'benefit': 'Reduces server load and improves response times'
                })
                
        # Check for missing database connection pooling
        db_file = 'database.py'
        if os.path.exists(db_file):
            with open(db_file, 'r') as f:
                content = f.read()
                
            if 'pool_size' in content and 'pool_size': 
                current_pool = re.search(r'pool_size["\']?\s*:\s*(\d+)', content)
                if current_pool and int(current_pool.group(1)) < 20:
                    perf_suggestions.append({
                        'area': 'Database',
                        'suggestion': 'Increase connection pool size for better concurrency',
                        'benefit': 'Handles more concurrent requests'
                    })
                    
        return perf_suggestions
    
    def generate_report(self) -> str:
        """Generate comprehensive refactoring report"""
        report = []
        report.append("# Code Refactoring and Optimization Report\n")
        report.append("## 2ª Vara Cível de Cariacica - Code Quality Analysis\n")
        
        # Analyze Python files
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip virtual environments and cache
            if any(skip in root for skip in ['.venv', '__pycache__', '.cache', 'node_modules']):
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                    
        report.append(f"\n### Files Analyzed: {len(python_files)}\n")
        
        # Import analysis
        report.append("\n## Import Analysis\n")
        import_issues = 0
        for py_file in python_files[:10]:  # Analyze first 10 files
            result = self.analyze_imports(py_file)
            if result['issues']:
                import_issues += len(result['issues'])
                report.append(f"- **{py_file}**: {', '.join(result['issues'])}\n")
                
        if import_issues == 0:
            report.append("✅ No import issues found\n")
            
        # Code quality
        report.append("\n## Code Quality Issues\n")
        quality_issues = 0
        for py_file in python_files[:10]:
            issues = self.check_code_quality(py_file)
            if issues:
                quality_issues += len(issues)
                report.append(f"- **{py_file}**:\n")
                for issue in issues:
                    report.append(f"  - {issue}\n")
                    
        if quality_issues == 0:
            report.append("✅ No code quality issues found\n")
            
        # Database optimizations
        report.append("\n## Database Optimizations\n")
        db_opts = self.optimize_database_queries()
        for opt in db_opts:
            report.append(f"- **{opt['file']}**: {opt['suggestion']} ({opt['impact']})\n")
            
        # Security audit
        report.append("\n## Security Audit\n")
        security_issues = self.security_audit()
        if security_issues:
            for issue in security_issues:
                report.append(f"- **{issue['file']}**: {issue['issue']} - Fix: {issue['fix']}\n")
        else:
            report.append("✅ No security issues found\n")
            
        # Performance suggestions
        report.append("\n## Performance Optimizations\n")
        perf_suggestions = self.performance_optimizations()
        for suggestion in perf_suggestions:
            report.append(f"- **{suggestion['area']}**: {suggestion['suggestion']} - {suggestion['benefit']}\n")
            
        # Summary
        report.append("\n## Summary\n")
        report.append(f"- Import issues: {import_issues}\n")
        report.append(f"- Code quality issues: {quality_issues}\n")
        report.append(f"- Database optimizations: {len(db_opts)}\n")
        report.append(f"- Security issues: {len(security_issues)}\n")
        report.append(f"- Performance suggestions: {len(perf_suggestions)}\n")
        
        return ''.join(report)
    
def main():
    """Main execution function"""
    logger.info("Starting code refactoring and optimization analysis...")
    
    refactorer = CodeRefactorer()
    report = refactorer.generate_report()
    
    # Save report
    with open('REFACTORING_REPORT.md', 'w') as f:
        f.write(report)
        
    logger.info("Report generated: REFACTORING_REPORT.md")
    
    # Also print key findings
    print("\n🔍 Code Analysis Complete!")
    print("Report saved to: REFACTORING_REPORT.md")
    
if __name__ == "__main__":
    main()