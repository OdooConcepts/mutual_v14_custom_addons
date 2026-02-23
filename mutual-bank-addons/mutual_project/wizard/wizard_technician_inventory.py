from odoo import models, fields, api


class WizardTechnicianInventory(models.TransientModel):
    _name = 'wiz.technician.inventory'
    _description = 'Generate Report for Technician Inventory'

    partner_id = fields.Many2one('res.partner', string='Technician')
    all_rec = fields.Boolean('Choose all Technicians', default=False)

    def fetch_record(self):
        partner_obj = self.env['res.partner']
        if not self.all_rec:
            products = self.env.cr.execute("""
                SELECT sw.code, sw.partner_id, sq.product_id, pt.name, SUM(sq.quantity) AS qty
                FROM stock_quant sq
                INNER JOIN stock_location sl ON sq.location_id = sl.id
                INNER JOIN stock_warehouse sw ON sl.id = sw.lot_stock_id
                INNER JOIN product_product pp ON sq.product_id = pp.id
                INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
                WHERE sq.quantity > 0 AND sw.partner_id = %s
                GROUP BY sw.code, sw.partner_id, sq.product_id, pt.name
            """, (self.partner_id.id,))
            return self.create_prod_list(products, 1)
        else:
            all_partners = partner_obj.search([('is_technician', '=', True)])
            all_ids = [partner.id for partner in all_partners]
            products = self.env.cr.execute("""
                SELECT sw.code, sw.partner_id, sq.product_id, pt.name, SUM(sq.quantity) AS qty
                FROM stock_quant sq
                INNER JOIN stock_location sl ON sq.location_id = sl.id
                INNER JOIN stock_warehouse sw ON sl.id = sw.lot_stock_id
                INNER JOIN product_product pp ON sq.product_id = pp.id
                INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
                WHERE sq.quantity > 0 AND sw.partner_id = %s
                GROUP BY sw.code, sw.partner_id, sq.product_id, pt.name
            """, (tuple(all_ids),))
            return self.create_prod_list(products, 2)

    def create_prod_list(self, products, all_or_one):
        new_sort_list = sorted(products, key=lambda k: (k['partner_id'], k['product_id']))
        return_list = []
        tech_name = str(new_sort_list[0]['code'])
        tech_id = str(new_sort_list[0]['partner_id'])
        prodlist = []

        if all_or_one == 2:
            for index, prod1 in enumerate(new_sort_list):
                if len(prodlist) == 0:
                    prodlist.append(prod1)
                for prod2 in new_sort_list[index + 1:]:
                    if tech_name == str(prod2["code"]) and prod2 not in prodlist:
                        prodlist.append(prod2)
                if tech_name != str(prod1['code']):
                    partner = self.env['res.partner'].browse(tech_id)
                    dict1 = {
                        'name': partner.name,
                        'designation': partner.function,
                        'city': partner.city,
                        'address': partner.street,
                        'items': prodlist
                    }
                    return_list.append(dict1)
                    tech_name = prod1['code']
                    tech_id = prod1['partner_id']
                    prodlist = []
            return return_list

        elif all_or_one == 1:
            for item in new_sort_list:
                prodlist.append(item)
            partner = self.env['res.partner'].browse(tech_id)
            dict1 = {
                'name': partner.name,
                'designation': partner.function,
                'city': partner.city,
                'address': partner.street,
                'items': prodlist
            }
            return [dict1]

    def print_report(self):
        return self.env.ref('mutual_project.action_report_technician_inventory').report_action(self)


