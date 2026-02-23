# -*- coding: utf-8 -*-

{
    'name': 'OC Sale product set',
    'category': 'mutual',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '1.0',
    'sequence': 150,
    'website': '',
    'summary': "Sale product set",
    'depends': [
        'sale','sales_team'
    ],
    'data': [
        'views/product_set.xml',
        'views/menuitems.xml',
        'wizard/product_set_add.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
       # 'demo/product_set.xml',
       # 'demo/product_set_line.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
