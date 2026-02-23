{
    'name': 'Mutual Requisition',
    'version': '1.0',
    'author': 'Ahsan',
    'depends': ['base_setup', 'helpdesk','mutual_project'],
    'data': [
        'security/ir.model.access.csv',
        'mutual_requisition_view.xml',
        'requisition_serial_number.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
