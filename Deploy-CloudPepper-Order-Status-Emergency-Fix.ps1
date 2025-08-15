# CloudPepper Emergency Fix for Order Status Override Missing Methods
# PowerShell Version - Fixes ParseError: action_return_to_previous is not a valid action on sale.order

Write-Host "🚨 CLOUDPEPPER EMERGENCY FIX - Order Status Override Missing Methods" -ForegroundColor Red
Write-Host "==================================================================" -ForegroundColor White

# Configuration
$ModuleName = "order_status_override"
$LocalPath = "d:\GitHub\osus_main\cleanup osus\odoo17_final"
$ModelFile = "$LocalPath\$ModuleName\models\sale_order.py"
$BackupDir = "$LocalPath\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "📁 Working with module: $ModuleName" -ForegroundColor Blue
Write-Host "📂 Local path: $LocalPath" -ForegroundColor Blue

try {
    # Create backup
    Write-Host "💾 Creating backup..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Copy-Item -Path "$LocalPath\$ModuleName" -Destination "$BackupDir\" -Recurse -Force
    Write-Host "✅ Backup created at: $BackupDir" -ForegroundColor Green
    
    # Check if model file exists
    if (!(Test-Path $ModelFile)) {
        Write-Host "❌ ERROR: Model file not found at $ModelFile" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🔍 Current model file found at: $ModelFile" -ForegroundColor Blue
    
    # Read current file content
    $content = Get-Content -Path $ModelFile -Raw -Encoding UTF8
    
    # Define missing methods
    $missingMethods = @"

    def action_return_to_previous(self):
        ""\"Return order to previous stage in workflow""\"
        self.ensure_one()
        
        # Get current status code
        current_code = self.custom_status_id.code
        
        # Define previous status mapping
        previous_status_map = {
            'documentation_progress': 'draft',
            'commission_progress': 'documentation_progress', 
            'final_review': 'commission_progress',
            'review': 'commission_progress'
        }
        
        if current_code not in previous_status_map:
            raise UserError(_("Cannot return to previous stage from current status."))
        
        # Find the previous status
        previous_code = previous_status_map[current_code]
        previous_status = self.env['order.status'].search([('code', '=', previous_code)], limit=1)
        if not previous_status:
            raise UserError(_("Previous status '%s' not found in the system.") % previous_code)
        
        # Change to previous status
        self._change_status(previous_status.id, _("Order returned to previous stage by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Order has been returned to previous stage: %s") % previous_status.name,
            subject=_("Order Returned to Previous Stage"),
            message_type='notification'
        )
        
        return True

    def action_request_documentation(self):
        ""\"Start the documentation process""\"
        self.ensure_one()
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_progress')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation progress status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation process started by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Documentation process has been started."),
            subject=_("Documentation Started"),
            message_type='notification'
        )
        
        return True
"@
    
    # Find insertion point after action_submit_for_review
    $pattern = 'def action_submit_for_review\(self\):.*?return True'
    $match = [regex]::Match($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    
    if (!$match.Success) {
        Write-Host "❌ ERROR: Could not find action_submit_for_review method" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🔧 Adding missing methods to model..." -ForegroundColor Yellow
    
    # Insert missing methods
    $newContent = $content.Replace($match.Value, $match.Value + $missingMethods)
    
    # Write updated content
    Set-Content -Path $ModelFile -Value $newContent -Encoding UTF8
    
    # Verify the fix
    Write-Host "🔍 Verifying the fix..." -ForegroundColor Yellow
    $updatedContent = Get-Content -Path $ModelFile -Raw -Encoding UTF8
    
    if ($updatedContent.Contains("def action_return_to_previous") -and 
        $updatedContent.Contains("def action_request_documentation")) {
        Write-Host "✅ Missing methods successfully added to model" -ForegroundColor Green
    } else {
        Write-Host "❌ ERROR: Methods not found after insertion" -ForegroundColor Red
        Write-Host "🔄 Restoring backup..." -ForegroundColor Yellow
        Copy-Item -Path "$BackupDir\$ModuleName\*" -Destination "$LocalPath\$ModuleName\" -Recurse -Force
        exit 1
    }
    
    Write-Host ""
    Write-Host "🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "==================================================================" -ForegroundColor White
    Write-Host "✅ Missing methods action_return_to_previous and action_request_documentation added" -ForegroundColor Green
    Write-Host "✅ Module should now install without ParseError" -ForegroundColor Green
    Write-Host "💾 Backup available at: $BackupDir" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🔄 Next steps for CloudPepper deployment:" -ForegroundColor Cyan
    Write-Host "1. Upload the fixed module to CloudPepper server" -ForegroundColor White
    Write-Host "2. Restart Odoo service: sudo systemctl restart odoo" -ForegroundColor White
    Write-Host "3. Upgrade the module from Odoo Apps menu" -ForegroundColor White
    Write-Host "4. Test the functionality" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Changes made:" -ForegroundColor Cyan
    Write-Host "- Added action_return_to_previous method with workflow logic" -ForegroundColor White
    Write-Host "- Added action_request_documentation method for documentation process" -ForegroundColor White
    Write-Host "- Both methods include proper error handling and notifications" -ForegroundColor White
    
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if (Test-Path $BackupDir) {
        Write-Host "🔄 Restoring backup..." -ForegroundColor Yellow
        try {
            Copy-Item -Path "$BackupDir\$ModuleName\*" -Destination "$LocalPath\$ModuleName\" -Recurse -Force
            Write-Host "✅ Backup restored" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to restore backup: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    exit 1
}
