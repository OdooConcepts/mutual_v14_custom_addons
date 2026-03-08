from odoo import api, fields, models,_
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class Account(models.Model):
    _inherit = 'account.account'

    old_system_id = fields.Integer()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    old_system_id = fields.Integer()


class AccountfiscalYear(models.Model):
    _inherit = 'account.fiscal.year'

    old_system_id = fields.Integer()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ntn = fields.Char(related='partner_id.vat', string='NTN', store=True)


class AccountfiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    old_system_id = fields.Integer()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    print_with_letter_header = fields.Boolean('Print With Letter Head', default=False)
    cs_number = fields.Char(string='Cs Number', related='partner_id.cs_number')
    terms_conditions = fields.Selection([('Additional', 'Additional')],
                                        'Terms and Condition')
    sales_type = fields.Selection([('New Installation', 'New Installation'), ('Additional', 'Additional')],
                                  string='Sales Type')
    payment_received = fields.Boolean(string='Payment Received')


class AccountPayment(models.TransientModel):
    _inherit = 'account.payment.register'

    def get_monitoring_period_from(self):
        monitoring_from = self.env['account.move'].search(
            [('id', '=', self.env.context.get('active_id'))]).monitoring_period_from
        self.monitoring_period_from = monitoring_from

    def get_monitoring_period_to(self):
        monitoring_to = self.env['account.move'].search(
            [('id', '=', self.env.context.get('active_id'))]).monitoring_period_to
        self.monitoring_period_to = monitoring_to

    monitoring_period_from = fields.Date(compute='get_monitoring_period_from')
    monitoring_period_to = fields.Date(compute='get_monitoring_period_to')

    def _create_payment_vals_from_wizard(self):
        val = super()._create_payment_vals_from_wizard()
        val.update({
            'monitoring_period_from': self.monitoring_period_from,
            'monitoring_period_to': self.monitoring_period_to
        })
        return val


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    invoices = fields.Many2one('account.move')
    cs_number = fields.Char(related="partner_id.cs_number", store=True)
    monitoring_period_from = fields.Date(tracking=True)
    monitoring_period_to = fields.Date(tracking=True)
    follow_up_responsible = fields.Many2one('hr.employee', 'Follow up Responsible', tracking=True)
    follow_up_date = fields.Date(string='Follow up Date', tracking=True)
    assign_rider = fields.Many2one('hr.employee', 'Assign Rider', tracking=True)
    payment_received = fields.Boolean('Payment Received', tracking=True)
    payment_methods = fields.Selection([('online', 'Online'), ('cash', 'Cash'), ('cheque', 'Cheque')])
    cheque_number = fields.Char('Cheque Number', tracking=True)
    payment_amount = fields.Char('Payment Amount', tracking=True)
    payment_received_date = fields.Date(tracking=True)
    assign_rider_date = fields.Date()
    print_with_letter_header = fields.Boolean('Print With Letter Head', default=False)
    css = fields.Char(size=12, string='CS Number', related='partner_id.cs_number', readonly=True)
    uplink_date = fields.Date(size=20, related='partner_id.uplink_date', string='Uplink Date',
                              readonly=True)
    address_criteria = fields.Selection([('Monitoring Address', 'Monitoring Address'),
                                         ('Mailing Address', 'Mailing Address'),
                                         ('Temporary Address', 'Temporary Address')],
                                        'Address Criteria', store=True, default='Mailing Address')
    show_outstanding = fields.Boolean(string='Show Outstanding/Advance', default=True)

    @api.onchange('monitoring_period_from','monitoring_period_to')
    def compute_narration_pay_ref(self):
        for rec in self:
            if rec.monitoring_period_from and rec.monitoring_period_to:
                narration = 'This invoice covers the following period: {0} - {1}'.format(str(rec.monitoring_period_from),str(rec.monitoring_period_to))
                pay_ref = '{0} - Monitoring Period From {1} - {2}'.format(rec.name,str(rec.monitoring_period_from),str(rec.monitoring_period_to))
                rec.write({
                    'narration':narration,
                    #'payment_reference':pay_ref
                           })

    def get_subscription_type(self):
        for rec in self:
            subscription = self.env['sale.subscription'].sudo().search([('code','=',rec.invoice_origin)])
            if subscription:
                return subscription.subscription_type
            else:
                return False

    def get_outstanding_amount(self):
        for rec in self:
            if rec.get_subscription_type() == 'sms_service':
                return 0.0
            account_id = self.env['account.account'].sudo().search([('name','in',['Debtors','MTI Payable']),('company_id','=',rec.partner_id.company_id.id)])
            query = self.env.cr.execute("""select sum(debit-credit) as total
                     from account_move_line where partner_id=%s and account_id in %s and date<'%s' and parent_state='posted'""" % (rec.partner_id.id,tuple(account_id.ids),rec.invoice_date))
            result = self.env.cr.dictfetchall()[0]['total']
            if result == None:
                return 0
            return result


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    issue_id = fields.Integer('Complaint Id', related='task_id.id')
    status = fields.Many2one('project.task.type')
    employee_id = fields.Many2one(string='Assigned Tech')
    cs_number = fields.Char('Cs Number', related='partner_id.cs_number')
    name = fields.Char(string='Remarks')
    task_id = fields.Many2one(string='Complaint Title')
    technician_name_other = fields.Many2one('hr.employee', 'Assigned Tech')
    multi_tech_other = fields.Many2many('hr.employee', string='Other Tech')
    reason = fields.Char('Remarks')
    created_on = fields.Datetime('Created On')
    time_in = fields.Datetime('T/I')
    time_out = fields.Datetime('T/O')
    total_time_duration = fields.Char("T/T", compute="_compute_duration")

    @api.depends('time_in', 'time_out')
    def _compute_duration(self):
        for rec in self:
            if rec.time_in and rec.time_out:
                # set the date and time format
                date_format = "%Y-%m-%d %H:%M:%S"
                # convert string to actual date and time
                timeIn = datetime.strptime(str(rec.time_in), date_format)
                timeOut = datetime.strptime(str(rec.time_out), date_format)
                # find the difference between two dates
                diff = timeOut - timeIn
                # diff_in_float = diff.total_seconds()
                # h = diff_in_float // 3600
                # m = (diff_in_float % 3600) // 60
                rec.total_time_duration = diff
            else:
                rec.total_time_duration = ''
