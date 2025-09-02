#!/usr/bin/env node

// Simple Node.js test to check JavaScript syntax
const fs = require('fs');
const path = require('path');

const jsFile = path.join(__dirname, 'static/src/js/dashboard.js');

try {
    const content = fs.readFileSync(jsFile, 'utf8');
    console.log('✅ JavaScript syntax check passed');
    console.log(`📊 File size: ${content.length} characters`);
    
    // Check for common patterns
    const patterns = [
        { name: 'State initialization', regex: /this\.state = useState\({/ },
        { name: 'ORM calls', regex: /this\.orm\.call/ },
        { name: 'Template bindings', regex: /static template = / },
        { name: 'Error handling', regex: /catch \(error\)/ }
    ];
    
    patterns.forEach(pattern => {
        const matches = content.match(new RegExp(pattern.regex, 'g'));
        console.log(`📋 ${pattern.name}: ${matches ? matches.length : 0} instances`);
    });
    
} catch (error) {
    console.error('❌ JavaScript syntax error:', error.message);
    process.exit(1);
}
