from odoo import models, fields, api

class TechnicianReport(models.TransientModel):
    _name = 'technician.report'
    _description = 'Generate Report of Technician TimeIn/Out'

    technician_id = fields.Many2many('hr.employee', string='Technician')
    date_start = fields.Datetime(string='From')
    date_end = fields.Datetime(string='To')

    def get_details(self):
        tech_activities = []
        for tech in self.technician_id:
            complaints = self.env['tech.activities.issues'].search([
                ('date_start', '>=', self.date_start),
                ('date_end', '<=', self.date_end),
                ('technician_name', '=', tech.id)
            ])
            if complaints:
                tech_activities.append({
                    'technician': tech.name,
                    'complaints': complaints
                })
        return tech_activities

    def print_report(self):
        return self.env.ref('mutual_project.technician_report_pdf').report_action(self)
