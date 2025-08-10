import xml.etree.ElementTree as ET

tree = ET.parse('account_payment_final/views/payment_actions_minimal.xml')
actions = tree.findall('.//record[@model="ir.actions.act_window"]')
print(f'Found {len(actions)} window actions:')
for action in actions:
    action_id = action.get('id')
    name_field = action.find('.//field[@name="name"]')
    name = name_field.text if name_field is not None else 'Unknown'
    print(f'  ✅ {action_id}: {name}')
