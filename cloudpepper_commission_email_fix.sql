
# CloudPepper Commission Email Template Fix
# Generated on 2025-08-17 12:54:37

# This script addresses the AttributeError: 'purchase.order' object has no attribute 'agent1_partner_id'
# by implementing proper conditional logic in email templates.

UPDATE_QUERIES = {
    "disable_problematic_templates": """
        UPDATE mail_template 
        SET active = false 
        WHERE body_html LIKE '%object.agent1_partner_id%' 
        AND model = 'purchase.order'
        AND active = true;
    """,
    
    "update_automation_rules": """
        UPDATE base_automation 
        SET active = false 
        WHERE trigger = 'on_create_or_write' 
        AND model_id IN (
            SELECT id FROM ir_model WHERE model = 'purchase.order'
        )
        AND filter_domain LIKE '%agent1_partner_id%';
    """,
    
    "backup_original_templates": """
        CREATE TABLE IF NOT EXISTS mail_template_backup AS 
        SELECT *, NOW() as backup_date 
        FROM mail_template 
        WHERE body_html LIKE '%object.agent1_partner_id%';
    """
}

SAFE_TEMPLATE_CONTENT = """<div>
<div style="margin: 0; padding: 20px; font-family: Arial, sans-serif; color: #333333; line-height: 1.5; max-width: 600px;">
    <div style="background-color: #800020; padding: 25px; border-radius: 5px 5px 0 0; display: flex; justify-content: space-between; align-items: center;">
        <h2 style="box-sizing:border-box;line-height:1.2;font-weight:500;font-family:'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Ubuntu, 'Noto Sans', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';color: white; margin: 0; font-size: 22px; flex-grow: 1;">COMMISSION PAYOUT<br/>NOTIFICATION</h2>
        <img src="/logo.png" class="img img-fluid o_we_custom_image" style="display:inline-block;box-sizing:border-box;vertical-align:middle;width: 25%; max-width: 150px; height: auto; float: right;" width="25%" alt="OSUS Properties Logo"/>
    </div>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px;">
        <p style="margin:0px 0 20px 0;box-sizing:border-box;margin-bottom: 20px;">
            Dear <strong style="box-sizing:border-box;font-weight:bolder;color: #800020;">
                <!-- Safe field access with fallbacks -->
                <t t-if="hasattr(object, 'agent1_partner_id') and object.agent1_partner_id">
                    <t t-out="object.agent1_partner_id.name"/>
                </t>
                <t t-elif="hasattr(object, 'origin_so_id') and object.origin_so_id and hasattr(object.origin_so_id, 'agent1_partner_id') and object.origin_so_id.agent1_partner_id">
                    <t t-out="object.origin_so_id.agent1_partner_id.name"/>
                </t>
                <t t-else="">
                    <t t-out="object.partner_id.name"/>
                </t>
            </strong>,
        </p>
        
        <p style="margin:0px 0 20px 0;box-sizing:border-box;margin-bottom: 20px;">
            We are pleased to inform you that your commission for deal 
            <strong style="box-sizing:border-box;font-weight:bolder;color: #800020;">
                <!-- Safe project and unit access -->
                <t t-if="hasattr(object, 'origin_so_id') and object.origin_so_id">
                    <t t-out="object.origin_so_id.name"/>
                    <t t-if="hasattr(object, 'project_id') and object.project_id"> - <t t-out="object.project_id.name"/></t>
                    <t t-elif="hasattr(object.origin_so_id, 'project_id') and object.origin_so_id.project_id"> - <t t-out="object.origin_so_id.project_id.name"/></t>
                    <t t-if="hasattr(object, 'unit_id') and object.unit_id"> (<t t-out="object.unit_id.name"/>)</t>
                    <t t-elif="hasattr(object.origin_so_id, 'unit_id') and object.origin_so_id.unit_id"> (<t t-out="object.origin_so_id.unit_id.name"/>)</t>
                </t>
                <t t-else="">
                    <t t-out="object.name"/>
                </t>
            </strong> 
            has been processed and sent to 
            <strong style="box-sizing:border-box;font-weight:bolder;color: #800020;">
                <t t-if="hasattr(object, 'origin_so_id') and object.origin_so_id">
                    <t t-out="object.origin_so_id.partner_id.name"/>
                </t>
                <t t-else="">
                    Customer
                </t>
            </strong> 
            amounting to <strong style="box-sizing:border-box;font-weight:bolder;color: #800020;">
                <t t-out="format_amount(object.amount_total, object.currency_id)"/>
            </strong>.
        </p>
        
        <div style="background-color: #fff; border: 1px solid #e0e0e0; border-radius: 5px; padding: 15px; margin: 20px 0;">
            <h3 style="color: #800020; margin: 0 0 10px 0; font-size: 16px;">Commission Details:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-weight: bold;">Order:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;"><t t-out="object.name"/></td>
                </tr>
                <tr t-if="hasattr(object, 'origin_so_id') and object.origin_so_id">
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-weight: bold;">Original Sale Order:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;"><t t-out="object.origin_so_id.name"/></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-weight: bold;">Commission Amount:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0; color: #800020; font-weight: bold;">
                        <t t-out="format_amount(object.amount_total, object.currency_id)"/>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Status:</td>
                    <td style="padding: 8px 0; color: #28a745; font-weight: bold;">Processed</td>
                </tr>
            </table>
        </div>
        
        <p style="margin:0px 0 20px 0;box-sizing:border-box;margin-bottom: 20px;">
            We will keep you updated once we receive the payment confirmation and complete your payout process.
        </p>
        
        <p style="margin:0px 0 20px 0;box-sizing:border-box;margin-bottom: 20px;">
            Best regards,
        </p>
        
        <p style="margin:0px 0 20px 0;box-sizing:border-box;margin-bottom: 20px;">
            <strong style="box-sizing:border-box;font-weight:bolder;color: #800020;">OSUS Properties Finance Department</strong>
        </p>
    </div>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; text-align: center; font-size: 14px; color: #555555; border-top: 1px solid #e0e0e0;">
        <p style="margin:0px 0 0px 0;box-sizing:border-box;margin-bottom: 0;">
            If you have any questions, please feel free to <a href="mailto:finance@osusproperties.com" style="box-sizing:border-box;color: #800020; text-decoration: none;">contact us</a>.
        </p>
        <p style="margin: 10px 0 0 0; font-size: 12px; color: #888;">
            OSUS Properties - Your Trusted Real Estate Partner
        </p>
    </div>
</div>
</div>"""

# Instructions for CloudPepper:
# 1. Run the backup query first
# 2. Disable problematic templates
# 3. Create new safe templates using the SAFE_TEMPLATE_CONTENT
# 4. Update any automation rules that might trigger the error
# 5. Test with a sample purchase order
