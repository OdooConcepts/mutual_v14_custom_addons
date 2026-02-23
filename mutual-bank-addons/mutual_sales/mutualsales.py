from odoo import models, fields, api
import requests

from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    sim_type = fields.Selection([('calling','Calling'),('data','Data'),('dnc','Data and Calling'),('internet_modem','Internet Modem')],string='Sim Type')
    network_type = fields.Selection(
        [('jazz', 'Jazz'), ('ufone', 'Ufone'), ('zong', 'Zong'), ('telenor', 'Telenor')],
        string='Network Type')
    sim_number = fields.Char('Sim Number')
    is_employee = fields.Boolean('Is an Employee?')
    is_rider = fields.Boolean('Is a Rider?', help="Check if the contact is a company, otherwise it is a person")
    is_technician = fields.Boolean('Is a Technician?', help="Check if the contact is a company, otherwise it is a person")
    customer_branch_det = fields.One2many('customer.branch.details', 'customer_branch_details', 'Branch Details')
    customer_relatives = fields.One2many('customer.relatives', 'customer_r', 'Relative')
    cs_number = fields.Char('Cs Number', size=10, select=True, store=True, track_visibility='onchange')
    branch_code = fields.Char('Branch Code', size=10, select=True, store=True, track_visibility='onchange')
    bank_code = fields.Char('Bank Code', size=10, select=True, store=True, track_visibility='onchange')
    uplink_date = fields.Date('Uplink Date', select=True, store=True, track_visibility='onchange')
    c_street = fields.Char('Corresponding Street', select=True, store=True)
    office = fields.Char('Office Number', select=True, store=True)
    c_street2 = fields.Char('Corresponding Street2', select=True, store=True)
    c_zip = fields.Char('Zip', change_default=True, size=24, select=True, store=True)
    c_city = fields.Char('City')
    c_state_id = fields.Many2one("res.country.state", 'State')
    c_country_id = fields.Many2one('res.country', 'Country')
    guard_less_branch = fields.Selection([('Yes', 'Yes'), ('No', 'No')], 'Guard Less Branch', store=True, default='No')
    locker_available = fields.Selection([('Yes', 'Yes'), ('No', 'No')], 'Locker Available', store=True)
    saturday_open = fields.Selection([('Yes', 'Yes'), ('No', 'No')], 'Saturday Open', store=True)
    rf_id = fields.Char('RF_ID', select=True, store=True)
    force_code = fields.Char('Force Code', select=True, store=True)
    parent = fields.Boolean('Parent', store=True)
    customer_visit = fields.Boolean('Force Visit Required', store=True)
    cus_ntn_no = fields.Char('NTN', store=True)
    cus_strn_no = fields.Char('STRN', store=True)
    region = fields.Selection([('North', 'North'), ('South', 'South'), ('Central', 'Central'), ('None', 'None')],
                              'Region', store=True, required=True)

    @api.onchange('customer_visit')
    def new_visit(self):
        if self.customer_visit:
            r = requests.post("http://localhost:2020/createcustomer",
                              data={
                                  'name': self.name,
                                  'cs': self.cs_number,
                                  'bank_code': self.bank_code,
                                  'branch_code': self.branch_code,
                                  'street1': self.street,
                                  'street2': self.street2,
                                  'city': self.city
                              })

class CustomerRelatives(models.Model):
    _name = "customer.relatives"

    customer_r = fields.Many2one('res.partner', 'Customer')
    other = fields.Char('Name', size=64, store=True)
    relationship = fields.Char('Position', size=100, store=True)
    contact_1 = fields.Char('Contact#1', size=64, store=True)
    contact_2 = fields.Char('Contact#2', size=64, store=True)
    sms_alert = fields.Boolean('SMS alert', store=True)

class CustomerBranchDetails(models.Model):
    _name = "customer.branch.details"

    customer_branch_details = fields.Many2one('res.partner', 'Customer')
    guardname = fields.Char('Guard Name', size=64, store=True)
    number = fields.Char('Number', size=100, store=True)
    securityco = fields.Char('Security Co', size=64, store=True)

class ResUsers(models.Model):
    _inherit = "res.users"

    signature_image = fields.Binary('Signature', store=True)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_status = fields.Selection([
        ('None', 'None'),
        ('All Items Installed', 'All Items Installed'),
        ('Some Items Left', 'Some Items Left'),
        ('Additional Items Installed', 'Additional Items Installed')
    ], 'SO Status', store=True, default='None')
    details = fields.Many2one('stock.picking', store=True, string='Internal Move')
    installation_date = fields.Date('Installation Date', store=True)
    complaint_reference = fields.Char('Complaint reference', store=True, on_change='auto_select()')
    cs_number = fields.Char(related='partner_id.cs_number', string='CS Number', readonly=True)
    tcs_receipt = fields.Char('TCS/Receipt No.', store=True)
    tcs_delivery_status = fields.Char('TCS Delivery Status', store=True)
    dispatch_sheet_date = fields.Date('Dispatched Date', store=True)
    branch_code = fields.Char(related='partner_id.branch_code', string='Branch Code', readonly=True)
    customer_name = fields.Char(related='partner_id.name', string='Name', readonly=True)
    bank_code = fields.Char(related='partner_id.bank_code', string='Bank Code', readonly=True)
    region = fields.Char(related='partner_id.city', string='Region', readonly=True)
    remarks = fields.Text('Remarks', store=True)
    is_tech = fields.Boolean(related='partner_id.is_technician', string='Technician', readonly=True)
    warehouse_name = fields.Char(related='warehouse_id.code', string='WH Name', readonly=True)
    req_ref = fields.Many2one('mutual.requisition', store=True, string='Requisition Ref')
    comp_ref = fields.Many2one('project.issue', store=True, string='Complaint Ref')


    @api.onchange('complaint_reference', 'req_ref')
    def auto_select(self):
        if self.complaint_reference:
            complaint_id = self.env['helpdesk.ticket'].search([('id', '=', self.complaint_reference)])
            if complaint_id:
                self.env.cr.execute('select id from res_partner where id = any(select partner_id from helpdesk_ticket where id = %s)', (self.complaint_reference,))
                customer = self.env.cr.dictfetchall()
                partner_list = self.env['res.partner'].search([('id', '=', customer[0]['id'])])
                self.partner_id = complaint_id.partner_id.id
                self.comp_ref = complaint_id.id
            else:
                raise ValidationError('Complaint does not exist')
        if self.req_ref:
            self.dispatch_sheet_date = self.req_ref.date

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_cs_number = fields.Char(related='order_partner_id.cs_number', string='CS Number', readonly=True)
    order_bank_code = fields.Char(related='order_partner_id.bank_code', string='Bank Code', readonly=True)
    order_branch_code = fields.Char(related='order_partner_id.branch_code', string='Branch Code', readonly=True)
    order_dispatched_date = fields.Date(related='order_id.dispatch_sheet_date', string='Dispatched Date', readonly=True)
    order_installation_date = fields.Date(related='order_id.installation_date', string='Installation Date', readonly=True)
