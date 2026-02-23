from odoo import api, fields, models

class TicketRemarks(models.Model):
    _name = 'ticket.remarks'


    helpdesk_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Id')
    responsible_person = fields.Char(string='Responsible Person')
    client = fields.Char(string='Client')
    remarks = fields.Char(string='Remarks')