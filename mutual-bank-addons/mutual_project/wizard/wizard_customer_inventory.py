from odoo import models, fields, api


class WizardCustomerInventory(models.TransientModel):
    _name = 'wiz.customer.inventory'
    _description = 'Generate Report for Customer Inventory'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    def fetch_record(self):
        self.env.cr.execute("""
            SELECT stock_picking.origin, stock_picking.date, stock_picking.state,
                   stock_move.product_qty, stock_move.name 
            FROM stock_picking 
            INNER JOIN stock_move ON stock_picking.id = stock_move.picking_id 
            WHERE stock_picking.state = 'done' AND stock_picking.partner_id = %s
            ORDER BY stock_picking.origin ASC
        """, (self.partner_id.id,))
        products = self.env.cr.dictfetchall()
        return products

    def print_report(self):
        return self.env.ref('mutual_project.action_report_customer_inventory').report_action(self)

