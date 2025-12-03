#!/usr/bin/env python3
"""
Comprehensive Odoo 17 Module Quality Review
Reviews all modules in the workspace and generates a quality report.
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Dict, List, Tuple

class ModuleReviewer:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.results = []
        
    def get_all_modules(self) -> List[Path]:
        """Get all Odoo modules in workspace"""
        modules = []
        for item in self.workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if (item / '__manifest__.py').exists() or (item / '__openerp__.py').exists():
                    modules.append(item)
        return sorted(modules)
    
    def check_manifest(self, module_path: Path) -> Dict:
        """Check __manifest__.py file"""
        manifest_file = module_path / '__manifest__.py'
        if not manifest_file.exists():
            manifest_file = module_path / '__openerp__.py'
        
        if not manifest_file.exists():
            return {
                'exists': False,
                'version': None,
                'odoo17_compatible': False,
                'license': None,
                'depends': []
            }
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                manifest = ast.literal_eval(content)
            
            version = manifest.get('version', '')
            is_17 = version.startswith('17.0')
            
            return {
                'exists': True,
                'version': version,
                'odoo17_compatible': is_17,
                'license': manifest.get('license', 'Unknown'),
                'depends': manifest.get('depends', []),
                'installable': manifest.get('installable', True),
                'application': manifest.get('application', False),
                'auto_install': manifest.get('auto_install', False),
            }
        except Exception as e:
            return {
                'exists': True,
                'version': None,
                'odoo17_compatible': False,
                'error': str(e)
            }
    
    def check_python_files(self, module_path: Path) -> Dict:
        """Check Python code quality"""
        python_files = list(module_path.rglob('*.py'))
        
        total_files = len(python_files)
        syntax_errors = []
        deprecated_patterns = []
        has_api_decorators = False
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check syntax
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file.name}: {str(e)}")
                
                # Check for @api decorators
                if '@api.' in content:
                    has_api_decorators = True
                
                # Check for deprecated patterns
                if 'osv.osv' in content or 'osv.Model' in content:
                    deprecated_patterns.append(f"{py_file.name}: Old-style osv")
                if '@api.one' in content:
                    deprecated_patterns.append(f"{py_file.name}: @api.one deprecated")
                if '@api.returns' in content and 'self' in content:
                    deprecated_patterns.append(f"{py_file.name}: @api.returns may be deprecated")
                    
            except Exception as e:
                syntax_errors.append(f"{py_file.name}: Read error - {str(e)}")
        
        return {
            'total_files': total_files,
            'syntax_errors': syntax_errors,
            'deprecated_patterns': deprecated_patterns,
            'has_api_decorators': has_api_decorators,
            'quality_score': max(0, 100 - (len(syntax_errors) * 20) - (len(deprecated_patterns) * 10))
        }
    
    def check_xml_files(self, module_path: Path) -> Dict:
        """Check XML/QWeb files"""
        xml_files = list(module_path.rglob('*.xml'))
        
        total_files = len(xml_files)
        parsing_errors = []
        deprecated_attrs = []
        modern_syntax = []
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Check for deprecated attrs syntax
                for elem in root.iter():
                    if 'attrs' in elem.attrib:
                        deprecated_attrs.append(f"{xml_file.name}: attrs={{}} deprecated")
                    if 'states' in elem.attrib and elem.tag == 'button':
                        deprecated_attrs.append(f"{xml_file.name}: states= on button deprecated")
                    
                    # Check for modern syntax
                    if 'invisible' in elem.attrib or 'readonly' in elem.attrib:
                        if not elem.attrib.get('invisible', '').startswith('{') and \
                           not elem.attrib.get('readonly', '').startswith('{'):
                            modern_syntax.append(xml_file.name)
                            
            except ET.ParseError as e:
                parsing_errors.append(f"{xml_file.name}: {str(e)}")
            except Exception as e:
                parsing_errors.append(f"{xml_file.name}: Read error")
        
        has_modern = len(set(modern_syntax)) > 0
        has_deprecated = len(deprecated_attrs) > 0
        
        return {
            'total_files': total_files,
            'parsing_errors': parsing_errors,
            'deprecated_attrs': list(set(deprecated_attrs))[:5],  # Limit output
            'has_modern_syntax': has_modern,
            'quality_score': max(0, 100 - (len(parsing_errors) * 20) - (min(len(deprecated_attrs), 5) * 10))
        }
    
    def check_javascript_files(self, module_path: Path) -> Dict:
        """Check JavaScript/OWL files"""
        js_files = list(module_path.rglob('*.js'))
        
        total_files = len(js_files)
        has_owl = False
        has_jquery = False
        has_es6 = False
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if '@odoo/owl' in content or 'from "@odoo/owl"' in content:
                    has_owl = True
                if 'const ' in content or 'let ' in content or '=>' in content:
                    has_es6 = True
                if '$(document)' in content or '$.ajax' in content:
                    has_jquery = True
                    
            except Exception:
                pass
        
        return {
            'total_files': total_files,
            'has_owl': has_owl,
            'has_es6': has_es6,
            'has_jquery': has_jquery,
            'quality_score': 80 if has_owl else (60 if has_es6 else 40)
        }
    
    def check_structure(self, module_path: Path) -> Dict:
        """Check module structure"""
        required_dirs = ['models', 'views', 'security']
        optional_dirs = ['static', 'data', 'controllers', 'reports', 'tests']
        
        has_required = sum(1 for d in required_dirs if (module_path / d).exists())
        has_optional = sum(1 for d in optional_dirs if (module_path / d).exists())
        
        has_security = (module_path / 'security' / 'ir.model.access.csv').exists()
        has_readme = (module_path / 'README.md').exists() or (module_path / 'README.rst').exists()
        has_init = (module_path / '__init__.py').exists()
        
        structure_score = (has_required / len(required_dirs)) * 60 + \
                         (has_optional / len(optional_dirs)) * 20 + \
                         (has_security * 10) + \
                         (has_readme * 5) + \
                         (has_init * 5)
        
        return {
            'has_required_dirs': has_required,
            'has_optional_dirs': has_optional,
            'has_security': has_security,
            'has_readme': has_readme,
            'has_init': has_init,
            'quality_score': int(structure_score)
        }
    
    def calculate_scores(self, checks: Dict) -> Tuple[int, int, int, int]:
        """Calculate compatibility, quality, compliance, and overall scores"""
        
        # Compatibility Score (0-100%)
        manifest = checks['manifest']
        if manifest['odoo17_compatible']:
            compat_score = 100
        elif manifest['version'] and manifest['version'].startswith('16.'):
            compat_score = 70
        elif manifest['version'] and manifest['version'].startswith('15.'):
            compat_score = 50
        else:
            compat_score = 30
        
        # Adjust for deprecated patterns
        if checks['python']['deprecated_patterns']:
            compat_score -= min(30, len(checks['python']['deprecated_patterns']) * 10)
        if checks['xml']['deprecated_attrs']:
            compat_score -= min(20, len(checks['xml']['deprecated_attrs']) * 5)
        
        # Quality Score (0-100%)
        quality_score = (
            checks['python']['quality_score'] * 0.4 +
            checks['xml']['quality_score'] * 0.3 +
            checks['javascript']['quality_score'] * 0.3
        )
        
        # Compliance Score (0-100%)
        compliance_score = checks['structure']['quality_score']
        
        # Overall Score
        overall = int((compat_score * 0.35 + quality_score * 0.35 + compliance_score * 0.30))
        
        return int(compat_score), int(quality_score), int(compliance_score), overall
    
    def get_action_recommendation(self, overall_score: int, checks: Dict) -> str:
        """Recommend action based on score"""
        if overall_score >= 90:
            return 'KEEP'
        elif overall_score >= 80:
            return 'UPDATE'
        else:
            return 'DELETE'
    
    def get_critical_issues(self, checks: Dict) -> List[str]:
        """Extract critical issues"""
        issues = []
        
        if not checks['manifest']['odoo17_compatible']:
            issues.append(f"Not Odoo 17 compatible (version: {checks['manifest'].get('version', 'Unknown')})")
        
        if checks['python']['syntax_errors']:
            issues.append(f"Python syntax errors: {len(checks['python']['syntax_errors'])}")
        
        if checks['xml']['parsing_errors']:
            issues.append(f"XML parsing errors: {len(checks['xml']['parsing_errors'])}")
        
        if checks['python']['deprecated_patterns']:
            issues.append(f"Deprecated Python patterns: {len(checks['python']['deprecated_patterns'])}")
        
        if checks['xml']['deprecated_attrs']:
            issues.append(f"Deprecated XML attrs: {len(checks['xml']['deprecated_attrs'])}")
        
        if not checks['structure']['has_security']:
            issues.append("Missing security/ir.model.access.csv")
        
        return issues[:5]  # Limit to top 5 issues
    
    def review_module(self, module_path: Path) -> Dict:
        """Review a single module"""
        print(f"Reviewing {module_path.name}...", end='', flush=True)
        
        checks = {
            'manifest': self.check_manifest(module_path),
            'python': self.check_python_files(module_path),
            'xml': self.check_xml_files(module_path),
            'javascript': self.check_javascript_files(module_path),
            'structure': self.check_structure(module_path)
        }
        
        compat, quality, compliance, overall = self.calculate_scores(checks)
        action = self.get_action_recommendation(overall, checks)
        issues = self.get_critical_issues(checks)
        
        result = {
            'name': module_path.name,
            'overall_score': overall,
            'compatibility_score': compat,
            'quality_score': quality,
            'compliance_score': compliance,
            'action': action,
            'issues': issues,
            'checks': checks
        }
        
        print(f" {overall}% [{action}]")
        return result
    
    def review_all_modules(self):
        """Review all modules and generate report"""
        modules = self.get_all_modules()
        print(f"\n🔍 Found {len(modules)} modules to review\n")
        
        for module_path in modules:
            result = self.review_module(module_path)
            self.results.append(result)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive report"""
        # Sort by overall score (descending)
        self.results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Categorize modules
        keep_modules = [r for r in self.results if r['action'] == 'KEEP']
        update_modules = [r for r in self.results if r['action'] == 'UPDATE']
        delete_modules = [r for r in self.results if r['action'] == 'DELETE']
        
        # Generate report
        report = []
        report.append("=" * 100)
        report.append("COMPREHENSIVE ODOO 17 MODULE QUALITY REVIEW")
        report.append("=" * 100)
        report.append(f"\nTotal Modules Reviewed: {len(self.results)}")
        report.append(f"  ✅ KEEP (90%+): {len(keep_modules)}")
        report.append(f"  ⚠️  UPDATE (80-89%): {len(update_modules)}")
        report.append(f"  ❌ DELETE (<80%): {len(delete_modules)}")
        report.append("\n" + "=" * 100)
        report.append("\nDETAILED MODULE SCORES")
        report.append("=" * 100)
        
        for result in self.results:
            report.append(f"\n{result['name'].upper()}: Overall Score {result['overall_score']}%")
            report.append(f"  - Compatibility: {result['compatibility_score']}%")
            report.append(f"  - Quality: {result['quality_score']}%")
            report.append(f"  - Compliance: {result['compliance_score']}%")
            
            if result['issues']:
                report.append(f"  - Issues:")
                for issue in result['issues']:
                    report.append(f"    • {issue}")
            else:
                report.append(f"  - Issues: None")
            
            report.append(f"  - Action: {result['action']}")
        
        # Summary sections
        report.append("\n" + "=" * 100)
        report.append("MODULES TO DELETE (Score < 80%)")
        report.append("=" * 100)
        if delete_modules:
            for r in delete_modules:
                report.append(f"  - {r['name']} ({r['overall_score']}%)")
        else:
            report.append("  None - All modules scored 80% or higher!")
        
        report.append("\n" + "=" * 100)
        report.append("MODULES TO UPDATE (Score 80-89%)")
        report.append("=" * 100)
        if update_modules:
            for r in update_modules:
                report.append(f"  - {r['name']} ({r['overall_score']}%)")
        else:
            report.append("  None - All modules either excellent or need deletion")
        
        report.append("\n" + "=" * 100)
        report.append("MODULES TO KEEP (Score 90%+)")
        report.append("=" * 100)
        if keep_modules:
            for r in keep_modules:
                report.append(f"  - {r['name']} ({r['overall_score']}%) ✅")
        else:
            report.append("  None - All modules need work")
        
        report.append("\n" + "=" * 100)
        report.append("STATISTICS")
        report.append("=" * 100)
        avg_overall = sum(r['overall_score'] for r in self.results) / len(self.results)
        avg_compat = sum(r['compatibility_score'] for r in self.results) / len(self.results)
        avg_quality = sum(r['quality_score'] for r in self.results) / len(self.results)
        avg_compliance = sum(r['compliance_score'] for r in self.results) / len(self.results)
        
        report.append(f"  Average Overall Score: {avg_overall:.1f}%")
        report.append(f"  Average Compatibility: {avg_compat:.1f}%")
        report.append(f"  Average Quality: {avg_quality:.1f}%")
        report.append(f"  Average Compliance: {avg_compliance:.1f}%")
        
        report.append("\n" + "=" * 100)
        report.append("Review completed successfully!")
        report.append("=" * 100)
        
        # Write to file
        report_text = '\n'.join(report)
        report_file = self.workspace_path / 'MODULE_QUALITY_REVIEW_REPORT.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n\n📊 Report generated: {report_file}")
        print(report_text)
        
        # Also save JSON for programmatic access
        json_file = self.workspace_path / 'MODULE_QUALITY_REVIEW_REPORT.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_modules': len(self.results),
                    'keep_count': len(keep_modules),
                    'update_count': len(update_modules),
                    'delete_count': len(delete_modules),
                    'avg_overall': round(avg_overall, 1),
                    'avg_compatibility': round(avg_compat, 1),
                    'avg_quality': round(avg_quality, 1),
                    'avg_compliance': round(avg_compliance, 1),
                },
                'modules': self.results,
                'keep': [r['name'] for r in keep_modules],
                'update': [r['name'] for r in update_modules],
                'delete': [r['name'] for r in delete_modules],
            }, f, indent=2)
        
        print(f"📊 JSON report generated: {json_file}")


def main():
    workspace = Path(__file__).parent.parent
    reviewer = ModuleReviewer(str(workspace))
    reviewer.review_all_modules()


if __name__ == '__main__':
    main()
