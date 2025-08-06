#!/usr/bin/env python3
"""
CloudPepper Environment Checker for JotForm Webhook
This script checks what Python packages are available in your CloudPepper environment.
"""

import sys
import subprocess

def check_package(package_name):
    """Check if a Python package is available."""
    try:
        __import__(package_name)
        return True, "✅ Available"
    except ImportError:
        return False, "❌ Not available"

def check_command(command):
    """Check if a system command is available."""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True, "✅ Available"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "❌ Not available"

def main():
    print("🔍 CloudPepper Environment Analysis for JotForm Webhook")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Python Executable: {sys.executable}")
    print()
    
    # Check required packages
    print("📦 Required Python Packages:")
    packages = [
        ('flask', 'Flask web framework'),
        ('requests', 'HTTP requests library'),
        ('gunicorn', 'WSGI HTTP Server'),
        ('dotenv', 'Environment variables (.env file support)')
    ]
    
    all_available = True
    for package, description in packages:
        available, status = check_package(package)
        print(f"  {package:15} - {description:35} {status}")
        if not available:
            all_available = False
    
    print()
    
    # Check alternative packages
    print("🔄 Alternative Packages (if main ones not available):")
    alternatives = [
        ('http.server', 'Built-in HTTP server (Python standard library)'),
        ('urllib.request', 'Built-in HTTP client (Python standard library)'),
        ('os', 'Built-in OS interface (Python standard library)'),
        ('json', 'Built-in JSON handling (Python standard library)')
    ]
    
    for package, description in alternatives:
        available, status = check_package(package)
        print(f"  {package:15} - {description:35} {status}")
    
    print()
    
    # Check system commands
    print("🔧 System Commands:")
    commands = [
        ('pip3', 'Python package installer'),
        ('python3', 'Python 3 interpreter'),
        ('curl', 'HTTP client tool'),
        ('wget', 'Web file downloader')
    ]
    
    for command, description in commands:
        available, status = check_command(command)
        print(f"  {command:15} - {description:35} {status}")
    
    print()
    print("📋 Recommendations for CloudPepper:")
    
    if all_available:
        print("✅ All required packages are available! You can proceed with the standard setup.")
    else:
        print("⚠️  Some packages are missing. Here are your options:")
        print("   1. Contact CloudPepper support to install missing packages")
        print("   2. Use the lightweight version with only standard library")
        print("   3. Try installing with: pip3 install --user <package_name>")
    
    print()
    print("🚀 Next Steps:")
    print("   1. Configure your .env file with CloudPepper-specific settings")
    print("   2. Choose the appropriate webhook version based on available packages")
    print("   3. Test the webhook locally before deploying")

if __name__ == "__main__":
    main()
