from odoo import fields, models


class inheritSaleOrder(models.Model):
    _inherit = 'stock.picking'

    status = fields.Selection([('Stock Returned from Customer To Warehouse', 'Stock Returned from Customer To Warehouse'),
              ('Stock Returned from Customer To Technician', 'Stock Returned from Customer To Technician'),
              ('Stock Returned from Technician To Warehouse', 'Stock Returned from Technician  To Warehouse'),
              ('Stock Returned from Bank Warehouse', 'Stock Returned from Bank Warehouse'), ('None', 'None'),
               ], string='Status')