// Script to fix missing catch blocks in Odoo web assets
const fs = require('fs');
const path = require('path');

// Function to add catch blocks to JavaScript file
function fixMissingCatchBlocks(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Regular expression to find try blocks without corresponding catch or finally
        // This is a simplified approach and might need refinement
        const regex = /try\s*{[\s\S]*?}(?!\s*catch|\s*finally)/g;
        
        // Replace each try block without catch by adding a catch block
        const fixedContent = content.replace(regex, match => {
            return `${match} catch (error) { console.error('Caught error:', error); }`;
        });
        
        // Write the fixed content back to the file
        if (content !== fixedContent) {
            fs.writeFileSync(filePath, fixedContent);
            console.log(`Fixed missing catch blocks in ${filePath}`);
            return true;
        } else {
            console.log(`No issues to fix in ${filePath}`);
            return false;
        }
    } catch (error) {
        console.error(`Error processing file ${filePath}:`, error);
        return false;
    }
}

// Main function to fix specific files
function fixSpecificFiles() {
    const filesToFix = [
        path.join(__dirname, 'oe_sale_dashboard_17', 'static', 'src', 'js', 'dashboard.js'),
        path.join(__dirname, 'custom_sales', 'static', 'src', 'js', 'dashboard.js')
    ];
    
    let totalFixed = 0;
    
    filesToFix.forEach(file => {
        if (fs.existsSync(file)) {
            console.log(`Checking and fixing file: ${file}`);
            const fixed = fixMissingCatchBlocks(file);
            if (fixed) {
                totalFixed++;
            }
        } else {
            console.log(`File not found: ${file}`);
        }
    });
    
    console.log(`\nTotal files fixed: ${totalFixed}`);
}

// Run the fix
fixSpecificFiles();
