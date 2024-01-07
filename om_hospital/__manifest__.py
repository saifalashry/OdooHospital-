# -*- coding: utf-8 -*-


{
    'name': 'Hospital Management',
    'version': '1.0.0',
    'category': 'Hospital',
    'author': 'Reda Kassem',
    'summary': 'Hospital Management System',
    'description': """Hospital Management System""",
    'depends': ['mail', 'product', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/patient_tag_data.xml',
        'data/patient.tag.csv',
        'data/sequence_data.xml',
        'data/mail_template_data.xml',
        'data/cron.xml',
        'wizard/cancel_appointment_view.xml',
        'views/menu.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
        'views/female_patient_view.xml',
        'views/patient_tag_view.xml',
        'views/operation_view.xml',
        'views/odoo_playground_view.xml',
        'views/res_config_settings_views.xml',
        'report/sales_report_inherit2.xml',
        'report/patient_card.xml',
        'report/patient_details_template.xml',
        'report/report.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': True,
    'sequence': -100,
    'license': 'LGPL-3',
}
