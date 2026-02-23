# -*- coding: utf-8 -*-
from odoo import fields, models

import odoo.addons.decimal_precision as dp


class ProductSetLine(models.Model):
    _name = 'product.set.line'
    _description = 'Product set line'
    _rec_name = 'product_id'
    _order = 'sequence'

    product_id = fields.Many2one(
        'product.product',
        string=u"Product", required=True)
    quantity = fields.Float(
        string=u"Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    product_set_id = fields.Many2one(
        'product.set', 'Set', ondelete='cascade')
    sequence = fields.Integer(
        string='Sequence',
        required=True, default=0,
    )
