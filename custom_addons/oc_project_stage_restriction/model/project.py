from odoo import api, fields, models
from odoo.http import request


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    user_id = fields.Many2many('res.users')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    user_in_stage = fields.Boolean(compute='check_current_user_in_stage')
    user_id_stage = fields.Many2many(related='stage_id.user_id')

    def check_current_user_in_stage(self):
        for rec in self:
            if self.env.uid:
                for user in rec.stage_id.user_id:
                    if user.id == self.env.uid:
                        rec.user_in_stage = True
                    else:
                        rec.user_in_stage = False

    def check_current_user(self):
        for rec in self:
            if self.env.uid:
                rec.user_id_stage = self.env.uid
            else:
                rec.user_in_stage = False
