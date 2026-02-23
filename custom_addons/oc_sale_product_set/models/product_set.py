# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product set'

    name = fields.Char(u"Name", help=u"Product set name", required=True)
    set_line_ids = fields.One2many(
        'product.set.line', 'product_set_id', u"Products", copy=True)



