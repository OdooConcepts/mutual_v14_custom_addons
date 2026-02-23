from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

class ComplaintTitle(models.Model):
    _name = 'oc.complaint.title'
    _rec_name = 'complaint_title'

    complaint_title = fields.Char('Complaint')


class HelpDeskTicketInherit(models.Model):
    _inherit = 'helpdesk.ticket'

    complaint_title = fields.Many2one('oc.complaint.title', 'Complaint Title', required=True)
    other_complaint = fields.Many2many('oc.complaint.title')
    time_ids = fields.One2many('complaint.timesheet', 'ticket_id', string='Time In/Out')
    ticket_remarks_ids = fields.One2many('ticket.remarks', 'helpdesk_id', string='Remarks')
    client_name = fields.Char(string="Client Name")
    sale_order = fields.Many2one('sale.order', string="Sale Order")
    complaint_source = fields.Selection(
        [("By Anwar Zaib", "By Anwar Zaib"), ("By LSR", "By LSR"), ("By Email", "By Email"),
         ("By CMS", "By CMS"), ("Direct", "Direct")], string="Complaint Source", required=True)
    cs_number = fields.Char(string='CS Number')
    branch_code = fields.Char(string='Branch Code', tracking=True)
    bank_code = fields.Char(string='Bank Code', tracking=True)
    city = fields.Char(string='City')
    bank_address = fields.Char(string='Bank Address')

    # Tab Checking Criteria Fields
    zone1 = fields.Boolean(string='Zone1')
    zone2 = fields.Boolean(string='Zone2')
    zone3 = fields.Boolean(string='Zone3')
    zone4 = fields.Boolean(string='Zone4')
    zone5 = fields.Boolean(string='Zone5')
    zone6 = fields.Boolean(string='Zone6')
    zone7 = fields.Boolean(string='Zone7')
    zone8 = fields.Boolean(string='Zone8')
    zone9 = fields.Boolean(string='Zone9')

    panic = fields.Boolean(string='Panic')
    duress = fields.Boolean(string='Duress')
    medical = fields.Boolean(string='Medical')
    fire = fields.Boolean(string='Fire')

    gms_bental = fields.Selection([('GSM', 'GSM'), ('Bental', 'Bental')], string="GSM BENTAL")
    ptcl = fields.Char(string='PTCL', store=True)
    gsm_prepaid_postpaid = fields.Selection([('Prepaid', 'Prepaid'), ('Postpaid', 'Postpaid')],
                                            string="Prepaid/Postpaid", store=True)
    ptcl_dedicated_shared = fields.Selection([('Dedicated', 'Dedicated'), ('Shared', 'Shared')],
                                             string="Dedicated/Shared", store=True)
    response_check = fields.Selection([('True', 'True'), ('False', 'False')], string="Response Check", store=True)
    check_by_client = fields.Char(string='Check By Client', store=True)
    sms_count = fields.Integer(string="SMS Count", compute="_compute_sms_count")

    def _compute_sms_count(self):
        for rec in self:
            count = self.env['oc.sms'].search_count([('record_id', '=', rec.id)])
            rec.sms_count = count

    @api.onchange('complaint_title')
    def _onchange_complaint_title(self):
        self.name = self.complaint_title.complaint_title

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            if self.partner_id.cs_number:
                self.cs_number = self.partner_id.cs_number
            if self.partner_id.branch_code:
                self.branch_code = self.partner_id.branch_code
            if self.partner_id.bank_code:
                self.bank_code = self.partner_id.bank_code
            if self.partner_id.city:
                self.city = self.partner_id.city
            if self.partner_id.street:
                self.bank_address = self.partner_id.street
        else:
            self.cs_number = ''
            self.branch_code = ''
            self.bank_code = ''
            self.city = ''
            self.bank_address = ''

    def action_helpdesk_sms(self):
        return {
            'name': "SMS",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('record_id', '=', self.id)],
            'res_model': 'oc.sms',
            'targer': 'current',
        }