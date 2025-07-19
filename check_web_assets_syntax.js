// Script to check for missing catch blocks in Odoo web assets
const fs = require('fs');
const path = require('path');

// Function to search for JavaScript files in a directory recursively
function findJsFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
            findJsFiles(filePath, fileList);
        } else if (file.endsWith('.js') && !file.endsWith('.min.js')) {
            fileList.push(filePath);
        }
    });
    
    return fileList;
}

// Function to check if file has try blocks without catch or finally
function checkForMissingCatchBlocks(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Check if there are try blocks without corresponding catch or finally
        // This is a simplified check and might have false positives
        let inComment = false;
        let tryBlockStart = [];
        let tryBlocksWithoutCatch = [];
        
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Skip comments
            if (line.trim().startsWith('//') || line.trim().startsWith('/*')) {
                inComment = line.includes('/*') && !line.includes('*/');
                continue;
            }
            
            if (inComment) {
                if (line.includes('*/')) {
                    inComment = false;
                }
                continue;
            }
            
            // Check for try blocks
            if (line.includes('try') && line.includes('{')) {
                tryBlockStart.push(i + 1);
            }
            
            // Check for catch blocks
            if (line.includes('catch') && line.includes('{')) {
                if (tryBlockStart.length > 0) {
                    tryBlockStart.pop();
                }
            }
            
            // Check for finally blocks
            if (line.includes('finally') && line.includes('{')) {
                if (tryBlockStart.length > 0) {
                    tryBlockStart.pop();
                }
            }
            
            // If we find a closing bracket that might be the end of a try block without catch
            if (line.includes('}') && !line.includes('catch') && !line.includes('finally')) {
                if (tryBlockStart.length > 0) {
                    // Check the next few lines for catch or finally
                    let hasCatchOrFinally = false;
                    for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
                        if (lines[j].includes('catch') || lines[j].includes('finally')) {
                            hasCatchOrFinally = true;
                            break;
                        }
                    }
                    
                    if (!hasCatchOrFinally) {
                        tryBlocksWithoutCatch.push({
                            line: tryBlockStart[0],
                            code: lines[tryBlockStart[0] - 1]
                        });
                        tryBlockStart.shift();
                    }
                }
            }
        }
        
        if (tryBlocksWithoutCatch.length > 0) {
            console.log(`${filePath} has try blocks without catch or finally:`);
            tryBlocksWithoutCatch.forEach(block => {
                console.log(`  Line ${block.line}: ${block.code}`);
            });
            return tryBlocksWithoutCatch;
        }
    } catch (error) {
        console.error(`Error processing file ${filePath}:`, error);
    }
    
    return null;
}

// Main function to check Odoo modules
function checkOdooModules() {
    const moduleDirs = [
        'oe_sale_dashboard_17',
        'custom_sales',
        'osus_dashboard'
    ];
    
    let totalIssues = 0;
    
    moduleDirs.forEach(moduleDir => {
        const modulePath = path.join(__dirname, moduleDir);
        
        if (fs.existsSync(modulePath)) {
            console.log(`Checking module: ${moduleDir}`);
            
            const jsFiles = findJsFiles(modulePath);
            jsFiles.forEach(jsFile => {
                const issues = checkForMissingCatchBlocks(jsFile);
                if (issues) {
                    totalIssues += issues.length;
                }
            });
        } else {
            console.log(`Module ${moduleDir} not found`);
        }
    });
    
    console.log(`\nTotal issues found: ${totalIssues}`);
}

// Run the check
checkOdooModules();
