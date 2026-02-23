from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class complaintTimeSheet(models.Model):
    _name = 'complaint.timesheet'
    _description = 'This model is used to manage timesheet of technician on tickets'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket Title')
    complaint_marker = fields.Many2one('helpdesk.stage', string='Marker')
    stage_id = fields.Many2one('helpdesk.stage',related='ticket_id.stage_id',string='State')
    cs_number = fields.Char('CS Number',related='ticket_id.partner_id.cs_number')
    name = fields.Char(string='Remarks')
    technician_ids = fields.Many2many('hr.employee', string='Technician(s)')
    time_in = fields.Float('T/I')
    time_out = fields.Float('T/O')
    total_time = fields.Float("T/T")
    time_in_date = fields.Date(string="Date", store=True, default=fields.datetime.today().date())
    is_timeout_computed = fields.Boolean(string='Is TimeOut Computed?', default=False)
    
    @api.onchange('complaint_marker')
    def update_complaint_status(self):
        for rec in self:
            if rec.complaint_marker:
                rec.ticket_id.write({'stage_id':rec.complaint_marker.id})

    @api.onchange('time_out')
    def _compute_duration(self):
        for rec in self:
            if rec.time_in and rec.time_out:
                diff = rec.time_out - rec.time_in
                rec.write({'total_time':diff})

