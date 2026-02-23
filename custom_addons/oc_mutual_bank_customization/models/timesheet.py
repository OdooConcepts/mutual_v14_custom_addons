from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class complaintTimeSheet(models.Model):
    _name = 'complaint.timesheet'
    _description = 'This model is used to manage timesheet of technician on tickets'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket Title')
    stage_id = fields.Many2one('helpdesk.stage', string='State')
    cs_number = fields.Char('Cs Number',)
    name = fields.Char(string='Remarks')
    technician_ids = fields.Many2many('hr.employee', string='Technician(s)')
    time_in = fields.Float('T/I')
    time_out = fields.Float('T/O')
    total_time = fields.Char("T/T", compute="_compute_duration")


    @api.depends('time_in', 'time_out')
    def _compute_duration(self):
        for rec in self:
            if rec.time_in and rec.time_out:
                diff = rec.time_out - rec.time_in
                rec.total_time = diff
            else:
                rec.total_time = ''

    def action_send_sms(self):
        val = {
            'record_id': self.ticket_id.id,
            'mobile_no': self.env.user.work_phone,
            'message_body': self.get_msg(),
        }
        for rec in self.technician_ids:
            vals = {
                'record_id': self.ticket_id.id,
                'mobile_no': rec.work_phone,
                'message_body': self.get_msg(),
            }
            self.env['oc.sms'].create(vals)
            self.env['oc.sms'].create(val)

    def get_msg(self):
        if self.ticket_id.cs_number and self.ticket_id.bank_code and self.ticket_id.branch_code and self.ticket_id.bank_address and self.ticket_id.city:
            result = str(self.ticket_id.id) + "\n" + str(self.ticket_id.complaint_title.display_name) + "\n" + self.ticket_id.bank_code + "\n" + self.ticket_id.cs_number + "\n" + "BC" + self.ticket_id.branch_code + "\n" + self.ticket_id.bank_address + "\n" + self.ticket_id.city
            return result
        else:
            raise UserError(_("Information Incomplete, You must have full information before sending an SMS"))