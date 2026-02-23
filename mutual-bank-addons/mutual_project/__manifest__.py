# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PM and HelpDesk Customization',
    'version': '1.0',
    'author': 'Odoo Concepts',
    'category': 'Other',
    'website': "https://www.odooconcepts.com/",
    'summary': 'This module contains customization on project module and helpdesk.',
    'depends': [
        'base_setup',
        'hr',
        'project',
        'helpdesk',
        'sale_management',
        'mutual_sales',
    ],
    'description': """
Track multi-level projects, tasks, work done on tasks
=====================================================

This application allows an operational project management system to organize your activities into tasks and plan the work you need to get the tasks completed.

Gantt diagrams will give you a graphical representation of your project plans, as well as resources availability and workload.

Dashboard / Reports for Project Management will include:
--------------------------------------------------------

    """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_customer_inventory_view.xml',
        'wizard/wizard_technician_inventory_view.xml',
        'wizard/technician_report_pdf.xml',
        'customer_inventory_report.xml',
        'technician_inventory_report.xml',
        'mutualprojects_view.xml',
        'stock_return_view.xml',
        'faulty_devices_view.xml',
        'views/report_customer_inventory.xml',
        'views/report_technician_inventory.xml',
        'wizard/technician_report_view.xml',
        #'views/sms_report_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
