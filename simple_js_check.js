#!/usr/bin/env node

const fs = require('fs');

// Simple syntax check function
function checkJSSyntax(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        console.log(`Checking ${filePath}...`);
        
        // Basic syntax checks
        const lines = content.split('\n');
        let braceCount = 0;
        let parenCount = 0;
        let bracketCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Count braces, parentheses, brackets
            braceCount += (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
            parenCount += (line.match(/\(/g) || []).length - (line.match(/\)/g) || []).length;
            bracketCount += (line.match(/\[/g) || []).length - (line.match(/\]/g) || []).length;
        }
        
        if (braceCount !== 0) {
            console.log(`❌ Unmatched braces: ${braceCount}`);
            return false;
        }
        if (parenCount !== 0) {
            console.log(`❌ Unmatched parentheses: ${parenCount}`);
            return false;
        }
        if (bracketCount !== 0) {
            console.log(`❌ Unmatched brackets: ${bracketCount}`);
            return false;
        }
        
        console.log(`✅ Basic syntax OK`);
        return true;
        
    } catch (error) {
        console.log(`❌ Error reading file: ${error.message}`);
        return false;
    }
}

// Check our files
const files = [
    'account_payment_final/static/src/js/cloudpepper_console_optimizer.js',
    'account_payment_final/static/src/js/unknown_action_handler.js'
];

console.log('Basic JavaScript syntax validation:\n');

let allGood = true;
files.forEach(file => {
    const result = checkJSSyntax(file);
    allGood = allGood && result;
    console.log('---');
});

console.log(allGood ? '\n✅ All files passed basic validation' : '\n❌ Some files have issues');
