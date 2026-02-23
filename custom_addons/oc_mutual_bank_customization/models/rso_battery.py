from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError

class RSOBattery(models.Model):
    _name = 'rso.battery'
    _rec_name = 'id'

    type = fields.Selection([('customer', 'Customer'),('technician', 'Technician'), ('rso', 'RSO')], string="Type", index=True, default='rso')
    customer = fields.Many2one('res.partner', 'Technician Name' )
    technician = fields.Many2one('hr.employee', 'Technician Name')
    contact_no = fields.Char(string='Contact No')
    sms = fields.Char(string='SMS', size=160)
    state = fields.Selection([('inprogress', 'In Progress'), ('failed', 'Failed'), ('send', 'Send')], default='inprogress', required=True,tracking=True)
    sms_count = fields.Integer(string="SMS Count", compute="_compute_sms_count")

    def _compute_sms_count(self):
        for rec in self:
            count = self.env['oc.sms'].search_count([('record_id', '=', rec.id)])
            rec.sms_count = count

    def action_rso_battery_sms(self):
        return {
            'name': "SMS",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('record_id', '=', self.id)],
            'res_model': 'oc.sms',
            'targer': 'current',
        }

    def send_sms(self):
        if self.id:
            val = {
                'record_id': self.id,
                'mobile_no': self.env.user.work_phone,
                'message_body': self.sms,
            }
            for rec in self:
                vals = {
                    'record_id': self.id,
                    'mobile_no': self.contact_no,
                    'message_body': self.sms,
                }
                self.env['oc.sms'].create(vals)
                self.env['oc.sms'].create(val)
        else:
            raise UserError(_("First Create Low Battery/RSO SMS"))





