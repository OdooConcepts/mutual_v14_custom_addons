from odoo import models, fields


class InheritAccountInvoice(models.Model):
    _inherit = 'account.move'

    print_with_letter_header = fields.Boolean(string='Print With Letter Head', default=False)

