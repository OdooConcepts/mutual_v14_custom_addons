from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_total_discount_order_line(self):
        amount_total_before_discount = 0
        for line in self.order_line:
            subtotal = line.product_uom_qty * line.price_unit
            amount_total_before_discount += subtotal
        amount_after_discount = self.amount_untaxed
        self.discount_amount = amount_total_before_discount - amount_after_discount

    @api.depends('order_line.price_subtotal', 'discount_method', 'discount_value', 'amount_tax')
    def disc_amount(self):
        val = 0
        for rec in self:
            val = self.amount_tax
        if self.discount_criteria == 'After Tax':
            if self.discount_method == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_method == 'Percentage':
                amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        elif self.discount_criteria == 'Before Tax':
            if self.discount_method == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_method == 'Percentage':
                amount_to_dis = self.amount_untaxed * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        else:
            self.discounted_amount = 0

    @api.depends('order_line.price_subtotal', 'discount_method', 'discount_value', 'amount_tax')
    def _compute_amounts(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.order_line)
        val = 0
        if len(self) == 1:
            val = self.amount_tax
            if self.discount_criteria == 'After Tax':
                if self.discount_method == 'Fixed':
                    self.amount_total = self.amount_untaxed + val - self.discount_value
                elif self.discount_method == 'Percentage':
                    amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
                    self.amount_total = (self.amount_untaxed + val) - amount_to_dis
                else:
                    self.amount_total = self.amount_untaxed + val
            elif self.discount_criteria == 'Before Tax':
                if self.discount_method == 'Fixed':
                    the_value_before = self.amount_untaxed - self.discount_value
                    self.amount_total = the_value_before + val
                elif self.discount_method == 'Percentage':
                    amount_to_dis = (self.amount_untaxed) * (self.discount_value / 100)
                    self.amount_total = self.amount_untaxed + val - amount_to_dis
                else:
                    self.amount_total = self.amount_untaxed + val
            else:
                self.amount_total = self.amount_untaxed + val
        else:
            for rec in self:
                rec.amount_total = 0

    discount_amount = fields.Float('Discount', compute='_compute_total_discount_order_line')
    discounted_amount = fields.Float('Discounted Amount', compute='disc_amount')
    discount_criteria = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')],
                                         string='Discount Criteria')
    discount_method = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], 'Discount Method')
    discount_value = fields.Float('Discount Value')
    amount_total = fields.Float(compute='_compute_amounts')
