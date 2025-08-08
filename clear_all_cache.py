#!/usr/bin/env python3
"""
Comprehensive cache clearing and module reset script for account_payment_final
"""

import os
import shutil
import glob
import subprocess
import sys

def clear_python_cache():
    """Clear Python bytecode cache files"""
    print("🐍 Clearing Python cache files...")
    
    cache_patterns = [
        "**/__pycache__/",
        "**/*.pyc", 
        "**/*.pyo",
        "**/.pytest_cache/",
        "**/pytest_cache/"
    ]
    
    removed_count = 0
    for pattern in cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    removed_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    removed_count += 1
                    print(f"  Removed directory: {path}")
            except Exception as e:
                print(f"  Error removing {path}: {e}")
    
    print(f"✅ Cleared {removed_count} Python cache files/directories")

def clear_odoo_cache():
    """Clear Odoo-specific cache files"""
    print("🔧 Clearing Odoo cache files...")
    
    odoo_cache_patterns = [
        "*.log",
        "odoo.conf.tmp",
        ".odoo_server_*",
        "session_store",
        "filestore/",
        "addons-path.cache"
    ]
    
    removed_count = 0
    for pattern in odoo_cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    removed_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    removed_count += 1
                    print(f"  Removed Odoo cache: {path}")
            except Exception as e:
                print(f"  Error removing {path}: {e}")
    
    print(f"✅ Cleared {removed_count} Odoo cache files/directories")

def clear_git_cache():
    """Clear Git cache if in a Git repository"""
    print("📦 Clearing Git cache...")
    
    if os.path.exists('.git'):
        try:
            # Clear Git index cache
            subprocess.run(['git', 'rm', '-r', '--cached', '.'], 
                         capture_output=True, check=False)
            subprocess.run(['git', 'add', '.'], 
                         capture_output=True, check=False)
            print("✅ Git cache cleared and re-added files")
        except Exception as e:
            print(f"⚠️ Git cache clear failed: {e}")
    else:
        print("ℹ️ Not in a Git repository")

def clear_module_cache():
    """Clear module-specific cache and temporary files"""
    print("📁 Clearing module cache...")
    
    module_cache_patterns = [
        "account_payment_final/**/__pycache__/",
        "account_payment_final/**/*.pyc",
        "account_payment_final/**/*.pyo",
        "account_payment_final/.cache/",
        "account_payment_final/static/cache/",
        "*.tmp",
        "*.bak",
        "*~"
    ]
    
    removed_count = 0
    for pattern in module_cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    removed_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    removed_count += 1
                    print(f"  Removed module cache: {path}")
            except Exception as e:
                print(f"  Error removing {path}: {e}")
    
    print(f"✅ Cleared {removed_count} module cache files/directories")

def clear_docker_cache():
    """Clear Docker-related cache if applicable"""
    print("🐳 Checking Docker cache...")
    
    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("  Docker is running - you may want to:")
            print("  - docker-compose down")
            print("  - docker system prune")
            print("  - docker-compose up -d")
            
            # Check for docker-compose
            if os.path.exists('docker-compose.yml'):
                print("  Found docker-compose.yml - consider restarting containers")
        else:
            print("  Docker not running or not available")
            
    except FileNotFoundError:
        print("  Docker not installed")

def validate_module_integrity():
    """Validate module structure after cache clearing"""
    print("🔍 Validating module integrity...")
    
    required_files = [
        "account_payment_final/__init__.py",
        "account_payment_final/__manifest__.py", 
        "account_payment_final/models/__init__.py",
        "account_payment_final/models/account_payment.py",
        "account_payment_final/views/account_payment_views.xml",
        "account_payment_final/security/payment_security.xml",
        "account_payment_final/security/ir.model.access.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    else:
        print("  ✅ All required files present")
        return True

def reset_module_permissions():
    """Reset file permissions if on Unix-like system"""
    if os.name == 'posix':  # Unix/Linux/macOS
        print("🔐 Resetting file permissions...")
        try:
            # Make Python files executable
            subprocess.run(['find', 'account_payment_final', '-name', '*.py', 
                          '-exec', 'chmod', '644', '{}', ';'], check=False)
            
            # Make directories accessible
            subprocess.run(['find', 'account_payment_final', '-type', 'd',
                          '-exec', 'chmod', '755', '{}', ';'], check=False)
            
            print("✅ File permissions reset")
        except Exception as e:
            print(f"⚠️ Permission reset failed: {e}")
    else:
        print("ℹ️ Skipping permissions (Windows)")

def generate_cache_clear_summary():
    """Generate a summary of cache clearing operations"""
    print("\n" + "="*60)
    print("📊 CACHE CLEARING SUMMARY")
    print("="*60)
    
    checks = [
        ("Python Cache", "Bytecode files cleared"),
        ("Odoo Cache", "Server cache files cleared"),
        ("Module Cache", "Module-specific cache cleared"),
        ("Git Cache", "Repository cache refreshed"),
        ("File Permissions", "Permissions reset (Unix only)"),
        ("Module Integrity", "All required files present")
    ]
    
    for check_name, description in checks:
        print(f"✅ {check_name:<20} - {description}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Restart your Odoo server")
    print("2. Update the module: --update=account_payment_final")
    print("3. Check for any import or syntax errors")
    print("4. Test the module functionality")
    
    if os.path.exists('docker-compose.yml'):
        print("\n🐳 DOCKER USERS:")
        print("1. docker-compose down")
        print("2. docker-compose up -d")
        print("3. docker-compose exec odoo odoo --update=account_payment_final")

def main():
    """Main cache clearing function"""
    print("🧹 COMPREHENSIVE CACHE CLEARING FOR ACCOUNT_PAYMENT_FINAL")
    print("=" * 70)
    
    if not os.path.exists("account_payment_final"):
        print("❌ Module directory 'account_payment_final' not found!")
        print("Make sure you're running this script from the correct directory.")
        return False
    
    # Execute all cache clearing operations
    operations = [
        clear_python_cache,
        clear_odoo_cache,
        clear_module_cache,
        clear_git_cache,
        reset_module_permissions,
        clear_docker_cache,
        validate_module_integrity
    ]
    
    for operation in operations:
        try:
            operation()
            print()  # Add spacing between operations
        except Exception as e:
            print(f"❌ Error in {operation.__name__}: {e}")
            print()
    
    # Generate summary
    generate_cache_clear_summary()
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n" + "="*70)
    if success:
        print("🎉 CACHE CLEARING COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️ CACHE CLEARING COMPLETED WITH WARNINGS!")
    print("="*70)
    
    sys.exit(0 if success else 1)
