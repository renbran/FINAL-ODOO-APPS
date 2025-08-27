#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 17 Workspace Cleanup Tool
Safely removes temporary files, cache, and cleanup scripts while preserving essential modules
"""

import os
import shutil
import glob
from pathlib import Path
import json
from datetime import datetime

class WorkspaceCleanupTool:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.essential_modules = self._find_essential_modules()
        self.cleanup_log = []
        
    def _find_essential_modules(self):
        """Find all directories with __manifest__.py (actual Odoo modules)"""
        modules = []
        
        # Directories to exclude (temporary deployment dirs)
        exclude_dirs = {
            'commission_ax_cloudpepper_deploy',
            'commission_ax_emergency_deploy',
            'deployment_package',
            'backups'
        }
        
        for item in self.workspace_path.iterdir():
            if (item.is_dir() and 
                (item / "__manifest__.py").exists() and 
                item.name not in exclude_dirs):
                modules.append(item.name)
        return modules
    
    def _log_action(self, action, path, size_mb=0):
        """Log cleanup actions"""
        self.cleanup_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'path': str(path),
            'size_mb': round(size_mb, 2)
        })
        print(f"{action}: {path} ({size_mb:.2f} MB)")
    
    def _get_size_mb(self, path):
        """Get size of file or directory in MB"""
        try:
            if Path(path).is_file():
                return Path(path).stat().st_size / (1024 * 1024)
            elif Path(path).is_dir():
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except (OSError, FileNotFoundError):
                            pass
                return total_size / (1024 * 1024)
        except (OSError, FileNotFoundError):
            return 0
        return 0
    
    def clean_pycache(self):
        """Remove all __pycache__ directories"""
        print("\n🧹 Cleaning Python cache directories...")
        pycache_dirs = list(self.workspace_path.rglob("__pycache__"))
        
        total_size = 0
        for pycache_dir in pycache_dirs:
            size = self._get_size_mb(pycache_dir)
            total_size += size
            
            try:
                shutil.rmtree(pycache_dir)
                self._log_action("REMOVED __pycache__", pycache_dir.relative_to(self.workspace_path), size)
            except Exception as e:
                print(f"❌ Error removing {pycache_dir}: {e}")
        
        return total_size
    
    def clean_pyc_files(self):
        """Remove all .pyc files"""
        print("\n🧹 Cleaning .pyc files...")
        pyc_files = list(self.workspace_path.rglob("*.pyc"))
        
        total_size = 0
        removed_count = 0
        for pyc_file in pyc_files:
            size = self._get_size_mb(pyc_file)
            total_size += size
            
            try:
                pyc_file.unlink()
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {pyc_file}: {e}")
        
        if removed_count > 0:
            self._log_action(f"REMOVED {removed_count} .pyc files", "workspace", total_size)
        
        return total_size
    
    def clean_temp_deployment_files(self):
        """Remove temporary deployment and validation files"""
        print("\n🧹 Cleaning temporary deployment files...")
        
        # Files that are safe to remove (temporary scripts and reports)
        temp_patterns = [
            "cloudpepper_*.py",
            "validate_*.py", 
            "emergency_*.py",
            "create_*.py",
            "deploy_*.py",
            "fix_*.py",
            "comprehensive_*.py",
            "additional_validation.py",
            "check_all_manifests.py",
            "burgundy_brand_validation.py",
            "crashpad_debug_resolver.py",
            "final_*.py",
            "manual_*.py",
            "modernize_*.py",
            "modern_syntax_updater.py",
            "module_analyzer.py",
            "nuclear_js_fix.py",
            "realtime_error_detector.py",
            "remove_duplicates.py",
            "simple_js_audit.py",
            "syntax_validator.py",
            "test_installation.py",
            "typeerror_fix_validator.py",
            "ultimate_cache_cleanup.ps1",
            "enhancement_validation.py",
            "js_*.py",
            "security_access_validator.py",
            "payment_*.py",
            "sales_*.py"
        ]
        
        total_size = 0
        for pattern in temp_patterns:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file():
                    size = self._get_size_mb(file_path)
                    total_size += size
                    
                    try:
                        file_path.unlink()
                        self._log_action("REMOVED temp script", file_path.name, size)
                    except Exception as e:
                        print(f"❌ Error removing {file_path}: {e}")
        
        return total_size
    
    def clean_temp_deployment_dirs(self):
        """Remove temporary deployment directories"""
        print("\n🧹 Cleaning temporary deployment directories...")
        
        temp_dirs = [
            "commission_ax_cloudpepper_deploy",
            "commission_ax_emergency_deploy", 
            "deployment_package",
            "backups"
        ]
        
        total_size = 0
        for dir_name in temp_dirs:
            dir_path = self.workspace_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                size = self._get_size_mb(dir_path)
                total_size += size
                
                try:
                    shutil.rmtree(dir_path)
                    self._log_action("REMOVED temp directory", dir_name, size)
                except Exception as e:
                    print(f"❌ Error removing {dir_path}: {e}")
        
        return total_size
    
    def clean_temp_files(self):
        """Remove temporary files"""
        print("\n🧹 Cleaning temporary files...")
        
        temp_file_patterns = [
            "*.zip",
            "*.log", 
            "*.txt",
            "*.sql",
            "*.json",
            "*.sh"
        ]
        
        # Files to keep (essential documentation and configs)
        keep_files = {
            ".gitignore",
            ".gitmodules", 
            "README.md",
            "requirements.txt"
        }
        
        total_size = 0
        for pattern in temp_file_patterns:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.name not in keep_files and file_path.is_file():
                    # Don't remove files inside module directories
                    if not any(module in str(file_path) for module in self.essential_modules):
                        size = self._get_size_mb(file_path)
                        total_size += size
                        
                        try:
                            file_path.unlink()
                            self._log_action("REMOVED temp file", file_path.name, size)
                        except Exception as e:
                            print(f"❌ Error removing {file_path}: {e}")
        
        return total_size
    
    def clean_markdown_reports(self):
        """Remove markdown report files but keep essential documentation"""
        print("\n🧹 Cleaning markdown report files...")
        
        # Keep essential documentation
        keep_markdown = {
            "README.md",
            "CHANGELOG.md",
            "LICENSE.md"
        }
        
        total_size = 0
        for md_file in self.workspace_path.glob("*.md"):
            if md_file.name not in keep_markdown:
                # Don't remove markdown files inside module directories
                if not any(module in str(md_file) for module in self.essential_modules):
                    size = self._get_size_mb(md_file)
                    total_size += size
                    
                    try:
                        md_file.unlink()
                        self._log_action("REMOVED report", md_file.name, size)
                    except Exception as e:
                        print(f"❌ Error removing {md_file}: {e}")
        
        return total_size
    
    def verify_essential_modules(self):
        """Verify that essential modules are still intact"""
        print("\n✅ Verifying essential modules...")
        
        for module in self.essential_modules:
            module_path = self.workspace_path / module
            manifest_path = module_path / "__manifest__.py"
            
            if not manifest_path.exists():
                print(f"❌ CRITICAL: {module}/__manifest__.py missing!")
                return False
            else:
                print(f"✅ {module} - intact")
        
        return True
    
    def generate_cleanup_report(self):
        """Generate cleanup report"""
        report_path = self.workspace_path / "WORKSPACE_CLEANUP_REPORT.json"
        
        total_size = sum(entry['size_mb'] for entry in self.cleanup_log)
        
        report = {
            'cleanup_timestamp': datetime.now().isoformat(),
            'total_size_cleaned_mb': round(total_size, 2),
            'files_cleaned': len(self.cleanup_log),
            'essential_modules_preserved': len(self.essential_modules),
            'essential_modules': self.essential_modules,
            'cleanup_actions': self.cleanup_log
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📊 Cleanup report saved: {report_path}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
        
        return report
    
    def run_cleanup(self):
        """Run complete workspace cleanup"""
        print("🚀 Starting Odoo 17 Workspace Cleanup")
        print("=" * 50)
        
        print(f"📁 Workspace: {self.workspace_path}")
        print(f"🔒 Essential modules: {len(self.essential_modules)}")
        
        # Run cleanup operations
        total_size = 0
        total_size += self.clean_pycache()
        total_size += self.clean_pyc_files()
        total_size += self.clean_temp_deployment_files()
        total_size += self.clean_temp_deployment_dirs()
        total_size += self.clean_temp_files()
        total_size += self.clean_markdown_reports()
        
        # Verify modules are intact
        if not self.verify_essential_modules():
            print("❌ CRITICAL ERROR: Some essential modules were damaged!")
            return False
        
        # Generate report
        report = self.generate_cleanup_report()
        
        print("\n" + "=" * 50)
        print("🎉 WORKSPACE CLEANUP COMPLETE!")
        print(f"📊 Total space freed: {total_size:.2f} MB")
        print(f"🗂️ Files cleaned: {len(self.cleanup_log)}")
        print(f"✅ Modules preserved: {len(self.essential_modules)}")
        print("\n✅ All essential Odoo modules remain intact!")
        
        return True

def main():
    """Main cleanup function"""
    workspace_path = Path.cwd()
    
    print("🧹 Odoo 17 Workspace Cleanup Tool")
    print("=" * 40)
    
    # Confirmation prompt
    print(f"📁 Workspace: {workspace_path}")
    print("\n⚠️ This will remove:")
    print("   - All __pycache__ directories")
    print("   - All .pyc files")
    print("   - Temporary deployment scripts")
    print("   - Validation and fix scripts")
    print("   - Report and log files")
    print("   - Temporary directories")
    
    print("\n✅ This will preserve:")
    print("   - All Odoo modules with __manifest__.py")
    print("   - Module source code and data files")
    print("   - Essential configuration files")
    
    confirm = input("\n🤔 Continue with cleanup? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Cleanup cancelled by user")
        return False
    
    # Run cleanup
    cleanup_tool = WorkspaceCleanupTool(workspace_path)
    success = cleanup_tool.run_cleanup()
    
    if success:
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n❌ Cleanup completed with errors!")
    
    return success

if __name__ == "__main__":
    main()
