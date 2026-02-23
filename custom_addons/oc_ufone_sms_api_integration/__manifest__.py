
# -*- coding: utf-8 -*-
#################################################################################
# Author      : Odoo Concepts. (<www.odooconcepts.com>)
# Copyright(c): 2019-Present Odoo Concepts.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Ufone SMS API Integration',
    'version': '1.0',
    'author': 'Odoo Concepts',
    'category': 'Other',
    'website': "https://www.odooconcepts.com/",
    'summary': 'Send sms using telenor API',
    'depends': ['base','project'],
    'data': [
        'data/scheduled_action_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/error_message_view.xml',
        'views/sms.xml'],
    'installable': True,
    'auto_install': False,
}
# 'data/scheduled_action_data.xml'