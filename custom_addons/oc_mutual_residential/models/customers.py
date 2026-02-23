from odoo import api, fields, models
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import re


class Product(models.Model):
    _inherit = 'product.template'

    old_system_id = fields.Integer()


class ProductVariant(models.Model):
    _inherit = 'product.product'

    old_system_id = fields.Integer()


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    old_system_id = fields.Integer()


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    old_system_id = fields.Integer()


class ProductTemplateAttributeline(models.Model):
    _inherit = 'product.template.attribute.line'

    old_system_id = fields.Integer()


class ProductVariant(models.Model):
    _inherit = 'product.product'

    old_system_id = fields.Integer()


class Company(models.Model):
    _inherit = 'res.company'

    old_system_id = fields.Integer()


class Customers(models.Model):
    _inherit = 'res.partner'

    old_system_id = fields.Integer()
    nic_num = fields.Char('CNIC Number')
    gst_num = fields.Char('GST Number')
    credit_card_no = fields.Char('Credit Card')
    credit_card_exp_date = fields.Date('Expiry Date')
    cs_category = fields.Selection([('DIS', 'DIS'),('CM', 'CM'), ('CN', 'CN'), ('LH', 'LH'), ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'),
                                    ('RES', 'RES')],
                                   string="CS Category")
    cs_number = fields.Char("CS Number")
    uplink_date = fields.Date("Uplink Date")
    office = fields.Char('Office Number', store=True)
    is_application_user = fields.Boolean(string="Is Application User?", default=False)
    vat = fields.Char(string='Ntn Number')
    c_street = fields.Char(string="Corresponding Street")
    c_street2 = fields.Char(string="Corresponding Street II")
    c_city = fields.Char(string="Corresponding City")
    contact_person = fields.Char(string="Contact Person")
    contact_person_details = fields.Char(string="Contact Person Details")
    temp_address = fields.Char(string="Temporary Address")

    @api.onchange('street','street2','city')
    def set_correspondance_address(self):
        for rec in self:
            if rec.street and rec.c_street== False:
                rec.write({'c_street':rec.street})
            if rec.street2 and rec.c_street2== False:
                rec.write({'c_street2':rec.street2})
            if rec.city and rec.c_city== False:
                rec.write({'c_city':rec.city})

    def write(self, vals):
        rec = super(Customers, self).name_get()
        if not vals.__contains__('is_company') and vals.__contains__('cs_number'):
            vals.update({'display_name': '[' + vals['cs_number'] + ']' + ' ' + self.name})
        res = super(Customers, self).write(vals)
        return res

    @api.constrains('cs_number')
    def _check_cs_uniqueness(self):
        for rec in self:
            if rec.cs_number:
                record = rec.search([('cs_number','=',rec.cs_number),('company_id','=',rec.env.company.id)])
                if len(record)>1:
                    raise ValidationError("You cannot assign same CS Number to two customers in the same company")

    # @api.constrains('phone')
    # def _check_phone_number(self):
    #      if self.phone:
    #         match = re.match('^[\d]{4}[\d]{7}$', self.phone)
    #         if match == None:
    #         raise ValidationError("Phone is not Valid")
    #    else:
    #      return False

    # @api.constrains('mobile')
    # def _check_mobile_number(self):
    #   if self.mobile:
    #      match = re.match('^[\d]{4}[\d]{7}$', self.mobile)
    #     if match == None:
    #        raise ValidationError("Mobile is not Valid")
    # else:
    #   return False

    @api.onchange('cs_category')
    def get_selection(self):
        if self.cs_category:
            self.write({'cs_number': self.cs_category})

    def name_get(self):
        res = []
        for partner in self:
            name = partner.name
            if partner.cs_number:
                name = "[%s] %s" % (partner.cs_number, partner.name)
            res += [(partner.id, name)]
        return res

    # def name_get(self):
    #     res = []
    #     for record in self:
    #         if record.cs_number:
    #             res.append((record.id, '[%s] %s' % (record.cs_number, record.name)))
    #         else:
    #             res.append((record.id, '%s' % (record.name)))
    #     return res

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = record.name or ''
    #         if record.cs_number:
    #             name += '[%s] %s' % (record.cs_number, record.name)
    #         name += (record.name or record.display_name) and (' ' + (record.name or record.display_name)) or ''
    #         result.append((record.id, name))
    #     return result
