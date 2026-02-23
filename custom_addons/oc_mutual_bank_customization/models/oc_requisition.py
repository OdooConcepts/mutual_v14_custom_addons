from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class OcRequisition(models.Model):
    _name = 'oc.requisition'
    _rec_name = 'serial_no'

    requisition_type = fields.Selection([('New Installation', 'New Installation'), ('Additional', 'Additional')],
                                        string='Requisition Type')
    serial_no = fields.Char(string='Requisition #', readonly=True, required=True, default=lambda *a: '/')

    title = fields.Text(string='Title')
    date = fields.Date(string='Date')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancel')],
                             default='draft', required=True, tracking=True)

    oc_requisition_line_ids = fields.One2many('oc.requisition.line', 'oc_requisition_id')

    def action_confirmed(self):
        self.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oc.requisition')
        vals['serial_no'] = sequence or '/'
        return super(OcRequisition, self).create(vals)
