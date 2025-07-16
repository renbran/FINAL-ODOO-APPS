{
    "name": "OM Dynamic Report",
    "version": "17.0.1.0.0",
    "author": "Your Company",
    "category": "Reporting",
    "summary": "Provides dynamic report generation capabilities.",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/om_dynamic_report_security.xml",
        "views/om_dynamic_report_views.xml",
        "views/om_dynamic_report_menu.xml",
        "data/om_dynamic_report_demo.xml"
    ],
    "demo": [
        "data/om_dynamic_report_demo.xml"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}
