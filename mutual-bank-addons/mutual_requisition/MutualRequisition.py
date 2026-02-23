from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class MutualRequisition(models.Model):
    _name = "mutual.requisition"
    _description = "Mutual Requisition"
    _rec_name = 'req_code'

    counter = fields.Integer('Counter', default=0)
    allow_req = fields.Boolean('Allow Requisition To Pass', default=False, store=True)
    req_code = fields.Char('Serial No.', readonly=True, store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State', default='draft', store=True)
    title = fields.Char('Title', store=True)
    date = fields.Date('Date', store=True, required=True)
    products = fields.One2many('basic.package.items', 'req_slip', 'Products', states={'confirmed': [('readonly', True)]})
    devices = fields.Char('Devices', compute='_compute_devices_details', store=True, size=15)
    qty = fields.Char('Qty', compute='_compute_devices_details', store=True, size=15)
    ref = fields.Char('Ref', compute='_compute_devices_details', store=True, readonly=True, size=15)
    ref_two = fields.Char('Ref', compute='_compute_devices_details', readonly=True)
    req_type = fields.Selection([('New Installation', 'New Installation'), ('Additional', 'Additional'), ('none', ' '),('Faulty', 'Faulty'),('Return To Warehouse', 'Return To Warehouse')], 'Requisition Type')
    all_recipiant = fields.Char('All Recipients', compute='_compute_devices_details', readonly=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get('req_type') == 'New Installation':
            vals['req_code'] = self.env['ir.sequence'].next_by_code('mutual.ni.requisition')
        elif vals.get('req_type') == 'Additional':
            vals['req_code'] = self.env['ir.sequence'].next_by_code('mutual.ad.requisition')
        return super(MutualRequisition, self).create(vals)

    @api.depends('products')
    def _compute_devices_details(self):
        for rec in self:
            devices = ''
            qty = ''
            ref = ''
            ref_two = ''
            all_recipiant = ''
            for line in rec.products:
                devices += line.courier_sheet_products.name + ","
                qty += str(line.quantity) + ","
                ref += str(line.cs_number) + ","
                ref_two += str(line.cs_number) + ","
                all_recipiant += str(line.customer.name) + ","
            rec.devices = devices.rstrip(',')
            rec.qty = qty.rstrip(',')
            rec.ref = ref.rstrip(',')
            rec.ref_two = ref_two.rstrip(',')
            rec.all_recipiant = all_recipiant.rstrip(',')

    def cancel(self):
        for rec in self:
            rec.write({'state': 'draft'})


    def confrm_date(self, curr_req_slip_date):
        for rec in self:
            check_date = rec.search_count([('date', '=', curr_req_slip_date)])
            if not check_date and rec.counter != 8:
                rec.counter += 1
                return rec.confrm_date(curr_req_slip_date - timedelta(days=1))
            else:
                return curr_req_slip_date

    def validate(self):
        alrt = []
        if not self.allow_req:
            date_list = [self.date - timedelta(days=1), self.date]
            date_list = [self.confrm_date(date_list[0]), date_list[1]]
            all_req = self.get_reqslp_data(date_list)
            pattern1, pattern2 = '', ''
            for index, item in enumerate(all_req):
                for item2 in all_req[index + 1:]:
                    if item["id"] != item2["id"] and item["cs"] == item2["cs"] and item["quantity"] == item2["quantity"] and item["name"] == item2["name"]:
                        pattern1 = f"({item['req_code']},{item2['req_code']}),"
                        pattern2 = f"({item2['req_code']},{item['req_code']}),"
                        if pattern1 not in alrt and pattern2 not in alrt:
                            alrt += pattern1
                    elif item["id"] != item2["id"] and item["quantity"] == item2["quantity"] and item["name"] == item2["name"] and item["partner_name"] == item2["partner_name"]:
                        pattern1 = f"({item['req_code']},{item2['req_code']}),"
                        pattern2 = f"({item2['req_code']},{item['req_code']}),"
                        if pattern1 not in alrt and pattern2 not in alrt:
                            alrt += pattern1
            for ind, item in enumerate(self.products):
                for item1 in self.products[ind + 1:]:
                    if item.courier_sheet_products.name == item1.courier_sheet_products.name and item.quantity == item1.quantity and item.cs_number == item1.cs_number and item.customer.name == item1.customer.name:
                        raise ValidationError('Multiple entries in this requisition')
            if alrt:
                alrt = alrt[:-1]
                raise ValidationError(f'Duplicate entries exist at id {alrt}')
            else:
                return self.write({'state': 'confirmed'})
        else:
            return self.write({'state': 'confirmed'})

    def get_reqslp_data(self, dt_lst):
        dv = ','.join(map(lambda x: f"'{x}'", dt_lst))
        self.env.cr.execute(f"""
            SELECT mr.id as id, mr.req_code as req_code, mr.allow_req as allow_req, bp.quantity as quantity,
                   bp.cs_number as cs, rp.name as partner_name, pi.name as name
            FROM mutual_requisition mr
            INNER JOIN basic_package_items bp ON mr.id = bp.req_slip
            INNER JOIN product_items pi ON bp.courier_sheet_products = pi.id
            INNER JOIN res_partner rp ON rp.id = bp.customer
            WHERE mr.date IN ({dv})
        """)
        return self.env.cr.dictfetchall()

    def cumm_product_data(self):
        cumm_prod = []
        for line in self.products:
            found = False
            for item in cumm_prod:
                if item['name'] == line.courier_sheet_products.name:
                    item['quantity'] += line.quantity
                    found = True
                    break
            if not found:
                cumm_prod.append({'name': line.courier_sheet_products.name, 'quantity': line.quantity})
        return cumm_prod


class BasicPackageItems(models.Model):
    _inherit = "basic.package.items"

    req_slip = fields.Many2one('mutual.requisition', 'Requisition Slip', store=True)
    req_code = fields.Char(related='req_slip.req_code', string='Req. Ref', readonly=True)
    issue_product_details = fields.Char(related='req_slip.title', string='Issue Product Details', readonly=True)
    date = fields.Date(related='req_slip.date', string='Issue Product Details', readonly=True)
