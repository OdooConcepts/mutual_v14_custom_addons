from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class OcRequisitionLine(models.Model):
    _name = 'oc.requisition.line'

    product_id = fields.Many2one('product.product', 'Product')
    type = fields.Selection([('for technician', 'For Technician'), ('for customer', 'For Customer')
                                , ('handover to warehouse', 'Handover To Warehouse')
                             ], string='Type')
    partner_id = fields.Many2one('res.partner', string="Customer/Technician")
    cs_number = fields.Char(string='CS Number')
    branch_code = fields.Char(string='Branch Code')
    location = fields.Char(string='Location')
    status = fields.Selection([('available', 'Available'), ('unavailable', 'Unavailable')
                             ], string='Status')
    ref = fields.Char(string='Reference')
    quantity = fields.Float(string='Quantity')
    oc_requisition_id = fields.Many2one('oc.requisition')


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            if self.partner_id.cs_number:
                self.cs_number = self.partner_id.cs_number
            if self.partner_id.branch_code:
                self.branch_code = self.partner_id.branch_code
            if self.partner_id.street:
                self.location = self.partner_id.street
        else:
            self.cs_number = ''
            self.branch_code = ''
            self.location = ''
