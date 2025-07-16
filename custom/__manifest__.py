{
    "name": "Custom Sales Order",
    "version": "17.0.1.0.0",
    "author": "Your Company",
    "category": "Sales",
    "summary": "Extends sale.order with custom fields and logic.",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "security/custom_security.xml",
        "views/custom_sales_order_views.xml",
        "views/custom_sales_order_menu.xml",
        "data/custom_sales_order_demo.xml"
    ],
    "demo": [
        "data/custom_sales_order_demo.xml"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}
