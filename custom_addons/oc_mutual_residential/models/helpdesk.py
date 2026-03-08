from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

class ComplaintTitle(models.Model):
    _name = 'oc.complaint.title'
    _rec_name = 'complaint_title'

    complaint_title = fields.Char('Complaint')

    @api.model
    def create(self, vals):
        if vals.get('complaint_title', 'New') == 'New':
            vals['complaint_title'] = self.env['ir.sequence'].next_by_code('oc.complaint.title') or 'New'
        result = super(ComplaintTitle, self).create(vals)
        return result


class inheritHelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    complaint_title = fields.Many2one('oc.complaint.title', 'Complaint Title', required=True)
    other_complaint = fields.Many2many('oc.complaint.title')
    responsible_person = fields.Char()
    contact_person = fields.Char()
    time_ids = fields.One2many('complaint.timesheet', 'ticket_id', string='Time In/Out')
    date_of_next_invoice = fields.Date(string='Date Of Next Invoice')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    is_period_change = fields.Selection([('yes','Yes'),('no','No')], string='Is monitoring period change?')
    reco_remarks = fields.Text(string='Reconnection Remarks')
    reason_of_disco = fields.Selection([
        ('no_need', 'NO NEED'),
        ('non_payment', 'NON PAYMENT'),
        ('house_sold_out', 'HOUSE SOLD OUT'),
        ('location_closed_permanently', 'LOCATION CLOSED PERMANENTLY'),
        ('new_owner_no_service', "NEW OWNER DON'T WANT OUR SERVICE"),
        ('tenant_no_service', "TENANT DON'T WANT OUR SERVICE"),
        ('customer_shift_abroad', 'CUSTOMER SHIFT ABROAD'),
        ('society_security_guard', 'SOCIETY ARRANGE SECURITY GUARD'),
        ('not_satisfied_service', 'NOT SATISFIED OUR SERVICE'),
        ('complaint_issue', 'COMPLAINT ISSUE'),
        ('system_hold', 'SYSTEM HOLD'),
        ('high_rate_not_affordable', 'HIGH RATE / NOT AFFORDABLE'),
        ('customer_shift_apartment', 'CUSTOMER SHIFT IN APPARTMENT'),
        ('house_demolish', 'HOUSE DEMOLISH'),
        ('system_not_available', 'SYSTEM NOT AVAILABLE'),
    ], string="Reason of Disconnection", tracking=True)
    is_disco = fields.Boolean('Is Disco?')

    @api.onchange('complaint_title')
    def set_is_disco(self):
        for rec in self:
            if rec.complaint_title:
                if rec.complaint_title.complaint_title in ['Disco','V/S DISCONNECT REQUIRED']:
                    rec.write({'is_disco':True})

    def do_active_customer(self, partner_id):
        self.env.cr.execute("""update res_partner set active=True where id=%s"""%(partner_id))
        return True

    def do_inactive_customer_and_subscription(self, partner_id):
        self.env.cr.execute("""update res_partner set active=False where id=%s"""%(partner_id))
        subscriptions = self.env['sale.subscription'].search([('partner_id','=',partner_id)])
        for subscription in subscriptions:
            subscription.set_close()

    @api.model
    def create(self, vals):
        result = super(inheritHelpdeskTicket, self).create(vals)
        if vals.get('partner_id'):
            if vals.get('name')=='Disco':
                self.do_inactive_customer_and_subscription(vals['partner_id'])
            elif vals.get('name')=='Reconnection':
                self.do_active_customer(vals['partner_id'])
        return result

    def get_super_userid(self):
        return SUPERUSER_ID

    @api.onchange('complaint_title')
    def _onchange_complaint_title(self):
        self.name = self.complaint_title.complaint_title

    @api.constrains('complaint_title','partner_id')
    def check_complaint(self):
        if not self.user_has_groups('oc_mutual_residential.disco_group') and self.name == 'Disco':
            raise ValidationError(_('The requested operation cannot be completed due to  restrictions.'))
        if self.search_count([('stage_id', '!=', 'Resolved'),('partner_id', '=', self.partner_id.id),('name','not in',['Disco','Reconnection','SMS Subscription'])])>1:
            raise ValidationError(_("Another complaint is already opened for this customer."))
        else:
            return False

