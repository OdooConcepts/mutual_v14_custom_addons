# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class error_message_wizard(models.TransientModel):
    _name = 'error.message.wizard'
    _description = 'Message wizard to display warnings, alert ,success messages'

    name = fields.Text(string='Message')

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    _defaults = {
        'name': get_default,
    }

