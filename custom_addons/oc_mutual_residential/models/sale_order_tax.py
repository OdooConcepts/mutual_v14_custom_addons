from odoo import api, fields, models


class SaleOrderTax(models.Model):

    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def tax_amount_all(self):
        for order in self:
            for line in order.order_line:
                if line.display_type != 'line_section' and line.tax_id.name == 'Sindh Revenue Board 19.5%':
                    order.tax_amount += line.price_subtotal * 19.5 / 100
            return order.tax_amount

    tax_amount = fields.Monetary(string='Taxes', compute='tax_amount_all')