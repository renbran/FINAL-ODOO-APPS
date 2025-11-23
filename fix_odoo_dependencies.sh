#!/bin/bash
###############################################################################
# Quick Odoo Dependencies Check and Fix
# Fixes common missing Python modules for Odoo 17
###############################################################################

echo "🔍 Checking Odoo Python Dependencies..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "Python version: $PYTHON_VERSION"
echo ""

# Common missing dependencies for Odoo 17
REQUIRED_PACKAGES=(
    "babel"
    "decorator"
    "docutils"
    "ebaysdk"
    "freezegun"
    "gevent"
    "greenlet"
    "idna"
    "Jinja2"
    "libsass"
    "lxml"
    "MarkupSafe"
    "num2words"
    "ofxparse"
    "passlib"
    "Pillow"
    "polib"
    "psutil"
    "psycopg2"
    "pydot"
    "pyopenssl"
    "pypdf2"
    "PyPDF2"
    "pyserial"
    "python-dateutil"
    "python-ldap"
    "python-stdnum"
    "pytz"
    "pyusb"
    "qrcode"
    "reportlab"
    "requests"
    "urllib3"
    "vobject"
    "Werkzeug"
    "xlrd"
    "XlsxWriter"
    "xlwt"
    "zeep"
)

echo "Checking for missing packages..."
MISSING=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package,,}" 2>/dev/null; then
        MISSING+=("$package")
        echo "  ✗ Missing: $package"
    fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "  ✓ All required packages are installed!"
else
    echo ""
    echo "Found ${#MISSING[@]} missing package(s)"
    echo ""
    read -p "Install missing packages now? [Y/n]: " install_choice

    if [ "$install_choice" != "n" ] && [ "$install_choice" != "N" ]; then
        echo ""
        echo "Installing missing packages..."

        # Install each missing package
        for package in "${MISSING[@]}"; do
            echo "Installing $package..."
            pip3 install "$package" -q
        done

        echo ""
        echo "✓ Installation complete!"

        # Verify babel specifically since that was the error
        if python3 -c "import babel.core" 2>/dev/null; then
            echo "✓ babel.core is now available"
        else
            echo "⚠️  babel.core still not available, trying reinstall..."
            pip3 install --force-reinstall babel
        fi
    fi
fi

echo ""
echo "Checking Odoo-specific packages..."

# Check for wkhtmltopdf (required for PDF reports)
if command -v wkhtmltopdf &> /dev/null; then
    echo "  ✓ wkhtmltopdf is installed"
else
    echo "  ✗ wkhtmltopdf is missing (required for PDF reports)"
    echo "    Install with: wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb && sudo apt install -y ./wkhtmltox_0.12.6-1.focal_amd64.deb"
fi

# Check for node/npm (required for some assets)
if command -v node &> /dev/null; then
    echo "  ✓ Node.js is installed: $(node --version)"
else
    echo "  ⚠️  Node.js is not installed (optional, but recommended)"
fi

echo ""
echo "================================================================"
echo "✓ Dependency check complete!"
echo "================================================================"
