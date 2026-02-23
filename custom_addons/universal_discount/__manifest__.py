# -*- coding: utf-8 -*-
{
    'name': "Discount",
    'summary': """
        Discount on invoice """,
    'description': """
             Settings -> general settings -> Companies
    """,
    'author': "",
    'website': " ",
    'images': ['static/description/Universal-Discount-V13.jpg'],
    'category': 'S',
    'version': '14.0',
    'name': "Universal Discount",
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'purchase', 'sale_management','account'],
    'data': [
         'data/data.xml',
        'views/ks_sale_order.xml',
        'views/ks_account_invoice.xml',
        'views/ks_purchase_order.xml',
        'views/ks_account_invoice_supplier_form.xml',
        'views/ks_account_account.xml',
        # 'views/ks_report.xml',
        'views/assets.xml',
    ],
}
