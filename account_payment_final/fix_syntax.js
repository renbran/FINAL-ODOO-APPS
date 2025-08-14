/**
 * JavaScript Syntax Error Fix Script
 * Fixes all semicolon placement issues in the JavaScript files
 */

const fs = require("fs");
const path = require("path");

const files = ["static/src/js/emergency_error_fix.js", "static/src/js/frontend/qr_verification.js"];

function fixSyntaxErrors(filePath) {
    console.log(`Fixing ${filePath}...`);

    let content = fs.readFileSync(filePath, "utf8");

    // Fix common syntax error patterns
    content = content
        // Fix semicolon after property in object
        .replace(/;\s*\}/g, "\n}")
        .replace(/;\s*\)/g, ")")
        .replace(/;\s*]/g, "]")
        .replace(/;\s*,/g, ",")
        // Fix semicolon at end of property definition
        .replace(/(['"])\s*;\s*\n/g, "$1\n")
        .replace(/:\s*(['"][^'"]*['"])\s*;\s*\n/g, ": $1\n")
        .replace(/:\s*([^;,}\]]+)\s*;\s*([,}\]])/g, ": $1$2")
        // Clean up extra semicolons in objects
        .replace(/,\s*;/g, ",")
        .replace(/}\s*;/g, "}")
        .replace(/]\s*;/g, "]")
        .replace(/\)\s*;/g, ")")
        // Fix specific patterns seen in errors
        .replace(/'.o_app\[data-menu-xmlid\*="expense"\]'\s*;/g, '".o_app[data-menu-xmlid*=\\"expense\\"]"')
        .replace(/day:\s*'numeric'\s*;/g, "day: 'numeric'");

    fs.writeFileSync(filePath, content, "utf8");
    console.log(`Fixed ${filePath}`);
}

// Fix all files
files.forEach(fixSyntaxErrors);

console.log("All syntax errors fixed!");
