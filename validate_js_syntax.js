const fs = require('fs');
const path = require('path');

// Function to validate JavaScript syntax
function validateJavaScript(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Remove Odoo-specific module declarations for syntax check
        const cleanContent = content
            .replace(/\/\*\* @odoo-module \*\*\//, '')
            .replace(/import .+ from .+;/g, '// import statement')
            .replace(/export .+/g, '// export statement');
        
        // Try to parse as JavaScript
        new Function(cleanContent);
        console.log(`✅ ${path.basename(filePath)}: Syntax OK`);
        return true;
    } catch (error) {
        console.log(`❌ ${path.basename(filePath)}: ${error.message}`);
        return false;
    }
}

// Files to validate
const jsFiles = [
    'account_payment_final/static/src/js/cloudpepper_console_optimizer.js',
    'account_payment_final/static/src/js/unknown_action_handler.js'
];

console.log('Validating JavaScript syntax...\n');

let allValid = true;
jsFiles.forEach(file => {
    const fullPath = path.join(__dirname, file);
    if (fs.existsSync(fullPath)) {
        const isValid = validateJavaScript(fullPath);
        allValid = allValid && isValid;
    } else {
        console.log(`❌ ${file}: File not found`);
        allValid = false;
    }
});

console.log(`\n${allValid ? '✅ All files passed syntax validation' : '❌ Some files have syntax errors'}`);
