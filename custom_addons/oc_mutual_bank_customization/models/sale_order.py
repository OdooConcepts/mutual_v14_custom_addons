from odoo import fields, models


class inheritSaleOrder(models.Model):
    _inherit = 'sale.order'
    # related fields on sales order TASK # 07
    cs_number_order = fields.Char(string='CS Number', related='partner_id.cs_number')
    branch_code_order = fields.Char(string='Branch Code', tracking=True, related='partner_id.branch_code')
    bank_code_order = fields.Char(string='Bank Code', tracking=True, related='partner_id.bank_code')
    region_order = fields.Selection([('None', 'None'), ('North', 'North'), ('South', 'South'), ('Central', 'Central')],
                                    default='None', string="Region", related='partner_id.region')

    complaint_ref_id = fields.Many2one('oc.complaint.title',string='Complaint Ref')
    installation_date = fields.Date(string='Installation Date')
    dispatched_date = fields.Date(string='Dispatched Date')
    so_status = fields.Selection([('none', 'None'),('all item installed', 'All Item Installed'),
                                  ('some item left', 'Some Item Left'), ('additional item installed', 'Additional Item Installed')
                                  ])

