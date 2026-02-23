from odoo import api, fields, models


class inheritAccount(models.Model):
    _inherit = 'account.move'
    cs_number = fields.Char(string='CS Number', size=6)
    branch_code = fields.Char(string='Branch Code', tracking=True)
    bank_code = fields.Char(string='Bank Code', tracking=True)
    invoice_ref = fields.Char(string='Invoice Reference', tracking=True)
    monitoring_period_from = fields.Date(string='Monitoring Period')
    monitoring_period_to = fields.Date(string='Monitoring Period')
    payment_status = fields.Selection([('Not Received', 'Not Received'), ('Received', 'Received')],
                                      default='Not Received', string="Payment Status")
    po_dd = fields.Selection([('PO', 'PO'), ('DD', 'DD')], string="PO/DD", store=True, track_visibility='onchange')
    cheque_number = fields.Char(string='Cheque #', tracking=True)
    cheque_date = fields.Date(string='Cheque Received Date', tracking=True)
    actual_amount = fields.Monetary(string='Actual Received Amount', tracking=True)


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.cs_number = self.partner_id.cs_number
            self.branch_code = self.partner_id.branch_code
            self.bank_code = self.partner_id.bank_code
        else:
            self.cs_number = ''
            self.bank_code = ''
            self.branch_code = ''

