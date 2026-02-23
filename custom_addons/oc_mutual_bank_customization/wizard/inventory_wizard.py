from odoo import _, fields, models
from odoo.exceptions import UserError


class InventoryReportWizard(models.TransientModel):
    _name = "inventory.report.wizard"
    _description = "Customer Inventory Report Wizard"

    partner_id = fields.Many2one('res.partner', string='Customer')
    # all_req = fields.Boolean("Choose all Technician")
    technician_id = fields.Many2many('res.partner',string='Technician',domain="[('is_technician','=', True)]")
    inventory_for = fields.Selection([('customer', 'Customer'), ('technician', 'Technician')], string="Inventory For?",required=True)
    search_criteria = fields.Selection([('specific', 'Specific'), ('all', 'All')], string="Search Criteria")


    def fetch_record(self):
        self.env.cr.execute("SELECT stock_picking.origin,stock_picking.date,stock_picking.status,"
                                "stock_move.product_qty,stock_move.name FROM stock_picking "
                                "INNER JOIN stock_move ON stock_picking.id = stock_move.picking_id "
                                "where stock_picking.state = 'done' and stock_picking.partner_id = "+str(self.partner_id.id) + "order by stock_picking.origin asc")
        products = self.env.cr.dictfetchall()
        return products    # returning products

    # technician report
    def get_record(self):
        return_list = []
        if self.technician_id:
            for ids in self.technician_id:
                id = ids.id
                self.env.cr.execute("""select sw.code,pt.name,sw.partner_id,sq.product_id,
                            pp.product_tmpl_id,sum(sq.quantity) 
                            as qty from stock_quant sq
                            inner join stock_location sl on sq.location_id=sl.id
                            inner join stock_warehouse sw on sl.id=sw.lot_stock_id
                            inner join product_product pp on sq.product_id=pp.id
                            inner join product_template pt on pt.id=pp.product_tmpl_id
                            where sq.quantity>0 and sw.partner_id in (""" + str(id) + ")" +
                                    " group by sw.code,sw.partner_id,sq.product_id,pp.product_tmpl_id,pt.name")
                products = self.env.cr.dictfetchall()
                if products:
                    rec = self.env['res.partner'].search([('id', '=', id)])
                    tech_info = {'name': rec.name, 'designation': rec.function, 'city': rec.city, 'address': rec.street,
                             'items': products,}
                    return_list.append(tech_info)
            return return_list
        else:
            technician_ids = self.env['res.partner'].search([('is_technician', '=', True)]).ids
            for id in technician_ids:
                self.env.cr.execute("""select sw.code,pt.name,sw.partner_id,sq.product_id,
                            pp.product_tmpl_id,sum(sq.quantity) 
                            as qty from stock_quant sq
                            inner join stock_location sl on sq.location_id=sl.id
                            inner join stock_warehouse sw on sl.id=sw.lot_stock_id
                            inner join product_product pp on sq.product_id=pp.id
                            inner join product_template pt on pt.id=pp.product_tmpl_id
                            where sq.quantity>0 and sw.partner_id in (""" + str(id) + ")" +
                                    " group by sw.code,sw.partner_id,sq.product_id,pp.product_tmpl_id,pt.name")
                products = self.env.cr.dictfetchall()
                if products:
                    rec = self.env['res.partner'].search([('id', '=', id)])
                    tech_info = {'name': rec.name, 'designation': rec.function, 'city': rec.city, 'address': rec.street,
                             'items': products,}
                    return_list.append(tech_info)
            return return_list
                # return self.get_tech_info(products,id)


    # def get_tech_info(self,products,id):
    #     return_list = []
    #     rec = self.env['res.partner'].search([('id', '=', id)])
    #     tech_info = {'name': rec.name, 'designation': rec.function, 'city': rec.city, 'address': rec.street,
    #                      'items': products,}
    #     return_list.append(tech_info)
    #     return return_list

    def action_print_report(self):
        if (self.inventory_for == 'customer'):
            return self.env.ref('oc_mutual_bank_customization.action_report_customer_inventory').report_action(self)
        if (self.inventory_for == 'technician'):
            return self.env.ref('oc_mutual_bank_customization.action_report_technician_inventory').report_action(self)
        else:
            raise UserError(_("Information Incomplete, First Select Inventory for"))