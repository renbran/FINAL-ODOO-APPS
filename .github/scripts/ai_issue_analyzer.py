#!/usr/bin/env python3
"""
Genspark AI Issue Analyzer
AI-powered analysis and assistance for GitHub issues
"""

import os
import sys
import json
import re
from datetime import datetime


class AIIssueAnalyzer:
    """AI-powered GitHub issue analysis and recommendations"""
    
    def __init__(self):
        self.issue_analysis = {
            'category': 'unknown',
            'priority': 'medium',
            'suggested_actions': [],
            'relevant_scripts': [],
            'estimated_difficulty': 'medium',
            'cloudpepper_impact': False
        }
    
    def categorize_issue(self, title, body):
        """AI categorization of issues"""
        combined_text = f"{title} {body}".lower()
        
        # CloudPepper deployment issues
        cloudpepper_keywords = ['cloudpepper', 'deployment', 'production', 'live', 'server']
        if any(keyword in combined_text for keyword in cloudpepper_keywords):
            self.issue_analysis['category'] = 'cloudpepper_deployment'
            self.issue_analysis['priority'] = 'high'
            self.issue_analysis['cloudpepper_impact'] = True
            return
        
        # Commission system issues
        commission_keywords = ['commission', 'payment', 'agent', 'broker', 'calculation']
        if any(keyword in combined_text for keyword in commission_keywords):
            self.issue_analysis['category'] = 'commission_system'
            self.issue_analysis['priority'] = 'high' if 'error' in combined_text else 'medium'
            return
        
        # JavaScript/Frontend issues
        frontend_keywords = ['javascript', 'js', 'owl', 'component', 'frontend', 'ui', 'interface']
        if any(keyword in combined_text for keyword in frontend_keywords):
            self.issue_analysis['category'] = 'frontend'
            self.issue_analysis['priority'] = 'high' if any(word in combined_text for word in ['crash', 'error', 'broken']) else 'medium'
            return
        
        # Database/Backend issues
        backend_keywords = ['database', 'model', 'field', 'orm', 'sql', 'migration']
        if any(keyword in combined_text for keyword in backend_keywords):
            self.issue_analysis['category'] = 'backend'
            self.issue_analysis['priority'] = 'high' if 'data loss' in combined_text else 'medium'
            return
        
        # Security issues
        security_keywords = ['security', 'access', 'permission', 'unauthorized', 'vulnerability']
        if any(keyword in combined_text for keyword in security_keywords):
            self.issue_analysis['category'] = 'security'
            self.issue_analysis['priority'] = 'high'
            return
        
        # Performance issues
        performance_keywords = ['slow', 'performance', 'timeout', 'optimization', 'speed']
        if any(keyword in combined_text for keyword in performance_keywords):
            self.issue_analysis['category'] = 'performance'
            self.issue_analysis['priority'] = 'medium'
            return
        
        # Bug reports
        bug_keywords = ['bug', 'error', 'exception', 'crash', 'fail', 'broken']
        if any(keyword in combined_text for keyword in bug_keywords):
            self.issue_analysis['category'] = 'bug'
            self.issue_analysis['priority'] = 'high' if any(word in combined_text for word in ['critical', 'urgent', 'production']) else 'medium'
            return
        
        # Feature requests
        feature_keywords = ['feature', 'enhancement', 'add', 'implement', 'new']
        if any(keyword in combined_text for keyword in feature_keywords):
            self.issue_analysis['category'] = 'feature_request'
            self.issue_analysis['priority'] = 'low'
            return
    
    def estimate_difficulty(self, title, body):
        """AI estimation of implementation difficulty"""
        combined_text = f"{title} {body}".lower()
        
        # High difficulty indicators
        high_difficulty = ['migration', 'refactor', 'rewrite', 'architecture', 'database schema']
        if any(indicator in combined_text for indicator in high_difficulty):
            self.issue_analysis['estimated_difficulty'] = 'high'
            return
        
        # Low difficulty indicators
        low_difficulty = ['typo', 'text', 'label', 'color', 'style', 'css', 'translation']
        if any(indicator in combined_text for indicator in low_difficulty):
            self.issue_analysis['estimated_difficulty'] = 'low'
            return
        
        # Medium is default
        self.issue_analysis['estimated_difficulty'] = 'medium'
    
    def suggest_relevant_scripts(self):
        """Suggest relevant emergency/validation scripts based on issue category"""
        category = self.issue_analysis['category']
        
        script_mapping = {
            'cloudpepper_deployment': [
                'cloudpepper_deployment_final_validation.py',
                'create_emergency_cloudpepper_fix.py',
                'create_commission_ax_emergency_deployment.py'
            ],
            'commission_system': [
                'create_commission_email_emergency_fix.py',
                'validate_commission_enhancement.py',
                'create_commission_ax_emergency_deployment.py',
                'commission_ax_emergency_cloudpepper_fix.py'
            ],
            'frontend': [
                'create_odoo17_attrs_emergency_fix.py',
                'emergency_odoo_define_global_fix.js',
                'test_odoo_define_fix.py'
            ],
            'backend': [
                'validate_commission_enhancement.py',
                'validate_order_net_commission.py',
                'final_order_net_commission_verification.py'
            ],
            'security': [
                'cloudpepper_deployment_final_validation.py',
                'comprehensive_module_analyzer.py'
            ],
            'performance': [
                'cloudpepper_deployment_final_validation.py',
                'workspace_cleanup_tool.py'
            ],
            'bug': [
                'create_simple_emergency_fix.py',
                'create_emergency_cloudpepper_fix.py'
            ]
        }
        
        self.issue_analysis['relevant_scripts'] = script_mapping.get(category, [
            'cloudpepper_deployment_final_validation.py'
        ])
    
    def generate_action_plan(self, title, body):
        """Generate AI-powered action plan"""
        category = self.issue_analysis['category']
        actions = []
        
        if category == 'cloudpepper_deployment':
            actions.extend([
                '1. Run deployment validation: `python cloudpepper_deployment_final_validation.py`',
                '2. Check CloudPepper logs for specific error messages',
                '3. Test locally with CloudPepper compatibility patches',
                '4. Use emergency fix scripts if critical issues found',
                '5. Validate with test deployment before production'
            ])
        
        elif category == 'commission_system':
            actions.extend([
                '1. Validate commission module: `python validate_commission_enhancement.py`',
                '2. Check email template configurations',
                '3. Test commission calculations with sample data',
                '4. Verify database field storage settings (store=True)',
                '5. Run emergency fix if email errors occur'
            ])
        
        elif category == 'frontend':
            actions.extend([
                '1. Check browser console for JavaScript errors',
                '2. Validate OWL component lifecycle handling',
                '3. Test with CloudPepper compatibility patches',
                '4. Review asset loading order in manifests',
                '5. Apply emergency JavaScript fixes if needed'
            ])
        
        elif category == 'backend':
            actions.extend([
                '1. Check Odoo server logs for Python errors',
                '2. Validate model field definitions',
                '3. Test database migrations in development',
                '4. Review security access rights',
                '5. Check for proper error handling in code'
            ])
        
        elif category == 'security':
            actions.extend([
                '1. Review security groups and access rights',
                '2. Check ir.model.access.csv files',
                '3. Validate record rules in security.xml',
                '4. Test with different user permission levels',
                '5. Run comprehensive security audit'
            ])
        
        elif category == 'performance':
            actions.extend([
                '1. Profile database queries for inefficiencies',
                '2. Check for N+1 query problems in loops',
                '3. Review computed field storage settings',
                '4. Optimize asset loading and caching',
                '5. Monitor CloudPepper resource usage'
            ])
        
        elif category == 'bug':
            actions.extend([
                '1. Reproduce the issue in development environment',
                '2. Check logs for error traces and stack dumps',
                '3. Identify the root cause of the problem',
                '4. Create minimal test case to verify fix',
                '5. Apply appropriate emergency fix script'
            ])
        
        elif category == 'feature_request':
            actions.extend([
                '1. Analyze requirements and scope',
                '2. Design solution architecture',
                '3. Check compatibility with existing modules',
                '4. Plan implementation phases',
                '5. Prepare CloudPepper deployment strategy'
            ])
        
        else:
            actions.extend([
                '1. Analyze issue details and gather more information',
                '2. Check relevant module documentation',
                '3. Review similar resolved issues',
                '4. Plan investigation approach',
                '5. Run general validation scripts'
            ])
        
        self.issue_analysis['suggested_actions'] = actions
    
    def generate_related_modules(self, title, body):
        """Identify related modules based on issue content"""
        combined_text = f"{title} {body}".lower()
        related_modules = []
        
        # Module keyword mapping
        module_keywords = {
            'commission_ax': ['commission', 'agent', 'broker', 'referrer'],
            'account_payment_approval': ['payment', 'approval', 'voucher'],
            'account_payment_final': ['payment', 'final', 'signature'],
            'order_net_commission': ['order', 'commission', 'net'],
            'enhanced_rest_api': ['api', 'rest', 'endpoint'],
            'oe_sale_dashboard_17': ['dashboard', 'sales', 'chart'],
            'crm_executive_dashboard': ['crm', 'dashboard', 'executive'],
            'statement_report': ['statement', 'report', 'customer']
        }
        
        for module, keywords in module_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                related_modules.append(module)
        
        return related_modules
    
    def create_issue_analysis_report(self, title, body):
        """Create comprehensive issue analysis report"""
        print(f"🤖 Analyzing issue: {title[:50]}...")
        
        # Run analysis
        self.categorize_issue(title, body)
        self.estimate_difficulty(title, body)
        self.suggest_relevant_scripts()
        self.generate_action_plan(title, body)
        
        related_modules = self.generate_related_modules(title, body)
        
        # Create report
        report = "### 🤖 Genspark AI Issue Analysis\n\n"
        
        # Issue classification
        category_emoji = {
            'cloudpepper_deployment': '☁️',
            'commission_system': '💰',
            'frontend': '🖥️',
            'backend': '⚙️',
            'security': '🔒',
            'performance': '⚡',
            'bug': '🐛',
            'feature_request': '✨',
            'unknown': '❓'
        }.get(self.issue_analysis['category'], '❓')
        
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(self.issue_analysis['priority'], '🟡')
        
        difficulty_emoji = {
            'high': '🔥',
            'medium': '⚖️',
            'low': '🟢'
        }.get(self.issue_analysis['estimated_difficulty'], '⚖️')
        
        report += f"**Category**: {category_emoji} {self.issue_analysis['category'].replace('_', ' ').title()}\n"
        report += f"**Priority**: {priority_emoji} {self.issue_analysis['priority'].title()}\n"
        report += f"**Estimated Difficulty**: {difficulty_emoji} {self.issue_analysis['estimated_difficulty'].title()}\n"
        
        if self.issue_analysis['cloudpepper_impact']:
            report += f"**CloudPepper Impact**: ☁️ Yes - May affect production deployment\n"
        
        report += "\n"
        
        # Action plan
        if self.issue_analysis['suggested_actions']:
            report += "#### 📋 Suggested Action Plan\n\n"
            for action in self.issue_analysis['suggested_actions']:
                report += f"{action}\n"
            report += "\n"
        
        # Relevant scripts
        if self.issue_analysis['relevant_scripts']:
            report += "#### 🔧 Relevant Emergency/Validation Scripts\n\n"
            for script in self.issue_analysis['relevant_scripts']:
                report += f"- `{script}`\n"
            report += "\n"
        
        # Related modules
        if related_modules:
            report += "#### 📦 Potentially Related Modules\n\n"
            for module in related_modules:
                report += f"- `{module}`\n"
            report += "\n"
        
        # CloudPepper specific guidance
        if self.issue_analysis['cloudpepper_impact']:
            report += "#### ☁️ CloudPepper Deployment Notes\n\n"
            report += "- Test fixes in staging environment first\n"
            report += "- Use emergency scripts for quick production fixes\n"
            report += "- Monitor logs after deployment\n"
            report += "- Have rollback plan ready\n"
            report += "- Check OSUS branding consistency\n\n"
        
        # Save report
        with open('ai_issue_analysis.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data
        analysis_data = self.issue_analysis.copy()
        analysis_data['related_modules'] = related_modules
        analysis_data['analyzed_at'] = datetime.now().isoformat()
        
        with open('ai_issue_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"✅ Issue analysis complete. Category: {self.issue_analysis['category']}")
        print(f"   Priority: {self.issue_analysis['priority']}, Difficulty: {self.issue_analysis['estimated_difficulty']}")
        
        return report


def main():
    """Main execution"""
    if len(sys.argv) < 3:
        print("Usage: python ai_issue_analyzer.py <title> <body>")
        sys.exit(1)
    
    title = sys.argv[1]
    body = sys.argv[2] if len(sys.argv) > 2 else ""
    
    analyzer = AIIssueAnalyzer()
    analyzer.create_issue_analysis_report(title, body)


if __name__ == "__main__":
    main()