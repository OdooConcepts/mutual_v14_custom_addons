from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re


class inheritResPartner(models.Model):
    _inherit = 'res.partner'
    cs_number = fields.Char(string='CS Number', size=7)
    branch_code = fields.Char(string='Branch Code', tracking=True)
    bank_code = fields.Char(string='Bank Code', tracking=True)
    uplink_date = fields.Date(string='Uplink Date')
    region = fields.Selection([('None', 'None'), ('North', 'North'), ('South', 'South'), ('Central', 'Central')],
                              default='None', string="Region")

    # TASK # 04
    ptcl1 = fields.Char(string='PTCL1')
    ptcl2 = fields.Char(string='PTCL2')
    ntn = fields.Char(string='NTN')
    strn = fields.Char(string='STRN')

    # Branch details section        TASK # 03
    guard_less_branch = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Guard Less Branch")
    locker_available = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Locker Available")
    saturday_open = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Saturday Open")

    is_technician = fields.Boolean(string="Is Technician?")

    # validation on cs_number       TASK # 02
    # @api.constrains('cs_number')
    # def check_cs_number(self):
    #     if self.cs_number:
    #         match = re.match('[A-Z][A-Z][\d][\d][\d][\d]', self.cs_number)
    #         if match == None:
    #             raise ValidationError("CS Number is not Valid")
    #         else:
    #             return False

    # override name_get method to concate cs_number with name           TASK # 06
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name
            if partner.cs_number:
                name = "[%s - %s] %s" % (partner.cs_number, partner.branch_code, partner.name)
            res += [(partner.id, name)]
        return res

    def write(self, vals):
        if not vals.__contains__('is_company') and vals.__contains__('cs_number'):
            vals.update({'display_name': '[' + vals['cs_number'] + ' - ' + self.branch_code + ']' + ' ' + self.name})
        elif not vals.__contains__('is_company') and vals.__contains__('branch_code'):
            vals.update({'display_name': '[' + self.cs_number + ' - ' + vals['branch_code'] + ']' + ' ' + self.name})
        elif not vals.__contains__('is_company') and vals.__contains__('branch_code') and vals.__contains__('cs_number'):
            vals.update({'display_name': '[' + vals['cs_number'] + ' - ' + vals['branch_code'] + ']' + ' ' + self.name})
        res = super(inheritResPartner, self).write(vals)
        return res
