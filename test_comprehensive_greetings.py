python3 -c "
import sys; sys.path.append('src')
import odoo; odoo.tools.config.parse_config([])
from odoo import api, SUPERUSER_ID
db_name = input('Database name: ')
with odoo.registry(db_name).cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    emp = env['hr.employee'].search([('work_email', '!=', False)], limit=1)
    if emp:
        print(f'Testing with employee: {emp.name} ({emp.work_email})')
        print(f'Employee has joining_date: {emp.joining_date if hasattr(emp, \"joining_date\") else \"Field not available\"}')
        for template_name in ['mail_template_birthday_personal', 'mail_template_birthday_announcement', 'mail_template_anniversary_personal', 'mail_template_anniversary_announcement']:
            try:
                template = env.ref(f'comprehensive_greetings.{template_name}')
                original_email = emp.work_email
                for test_email in ['renbranmadelo@gmail.com', 'salescompliance@osusproperties.com']:
                    emp.work_email = test_email
                    template.send_mail(emp.id, force_send=True)
                    print(f'✅ Sent {template_name} to {test_email}')
                emp.work_email = original_email
            except Exception as e:
                print(f'❌ {template_name}: {e}')
        env.cr.commit()
        print('🎉 All OSUS Greetings tests completed!')
    else:
        print('❌ No employees found with work email')
"
