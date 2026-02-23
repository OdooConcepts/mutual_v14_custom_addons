from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo import api
import re
import urllib.parse
from xml.dom.minidom import parseString
import requests


class smsIntegration(models.Model):
    _name = 'sms.integration'
    _rec_name = 'number'

    provider = fields.Selection([('ufone', 'Ufone'), ('jazz', 'Jazz')])
    url_api = fields.Char('Url Api')
    state = fields.Selection([('draft', 'Not Confirmed'),
                              ('done', 'Confirmed')], default='draft')
    customer_id = fields.Char('Customer ID', required=True)
    password = fields.Char('Password', required=True)
    mask = fields.Char('Mask', required=True)
    message = fields.Text('Message', default='Hello World....!')
    number = fields.Char('Number')
    message_type = fields.Selection([('Transactional', 'Transactional'), ('Nontransactional', 'Non-Transactional')],
                                    string='Message Type')
    count = fields.Integer(compute='count_message_length')
    sms_status = fields.Char()

    def count_message_length(self):
        self.count = len(self.message)

    def error_message(self, message):
        context = dict(self._context or {})
        context['message'] = message
        view_id = self.env['ir.model.data'].get_object_reference(
            'oc_ufone_sms_api_integration',
            'error_message_wizard')[1]

        return {
            'name': _('Message'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'error.message.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    # def sent_message(self):
    #   ''' Sends post request to get session Id against username & password '''
    #   customer_id = urllib.unquote(self.customer_id).encode('utf8')
    #  number = urllib.unquote(self.number).encode('utf8')
    #   password = urllib.unquote(self.password).encode('utf8')
    #  message = urllib.unquote(self.message).encode('utf8')
    #   mask = urllib.unquote(self.mask).encode('utf8')
    #   message_type = urllib.unquote(self.message_type).encode('utf8')
    #   url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=%s&message=%s&shortcode=%s&lang=English&mobilenum=%s&password=%s&groupname=&messagetype=%s"%(customer_id,message,mask,number,password,message_type))
    #  repsonse = requests.get(url,verify=False)
    #   result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
    #   if 'Successful' in result:
    #      self.write({'state':'done'})
    #   return result

    def smsSent(self):
        if self.number:
            if self.number and self.message:
                ''' Sends post request to get session Id against username & password '''
                sms_carrier = self.provider
                customer_id = urllib.parse.unquote(self.customer_id).encode('utf8')
                number = urllib.parse.unquote(self.number).encode('utf8')
                password = urllib.parse.unquote(self.password).encode('utf8')
                message = urllib.parse.quote(self.message).encode('utf8')
                mask = urllib.parse.unquote(self.mask).encode('utf8')
                url_api = urllib.parse.unquote(self.url_api).encode('utf8')
                if int(self.count) < 160:
                    if sms_carrier == 'ufone':
                        message_type = urllib.parse.unquote(self.message_type).encode('utf8')
                        url = (url_api % (
                            customer_id, message, mask, number, password, message_type))
                        repsonse = requests.get(url, verify=False)
                        result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
                        self.sms_status = result
                        # self.env['sms.report'].create(
                        #     {'to': number, 'sms': self.sms, 'status': result, 'type': 'RSO Message'})
                        self.state = 'done'
                        return result
                    elif sms_carrier == 'jazz':
                        url = (
                                url_api % (
                            customer_id, password, mask, number, message))
                        repsonse = requests.get(url, verify=False)
                        if repsonse.text == 'Message Sent Successfully!':
                            self.sms_status = repsonse.text
                            self.state = 'done'
                        else:
                            self.sms_status = repsonse.text
                            raise ValidationError(repsonse.text)

                        # self.env['sms.report'].create(
                        #
                        #         {'to': number, 'sms': self.sms, 'status': repsonse.text, 'type': 'RSO Message'})

                else:
                    raise ValidationError('Limit Exceed', 'SMS must be within 160 characters')
        else:
            raise ValidationError('Empty Field', 'Kindly enter mobile number of technician')


class SmsMain(models.Model):
    _name = 'oc.sms'
    _rec_name = 'message_body'

    state = fields.Selection(
        [('sending', 'Sending'),
         ('fail', 'Failed'), ('sent', 'Sent')], string='State', default='sending')
    mobile_no = fields.Char('Mobile Number')
    message_body = fields.Text('Message')
    sender_list = fields.Many2many('res.partner', string='Sender List')
    reason = fields.Char('Reason')
    record_id = fields.Integer(string='Record Id', invisible='1')

    def testMessage(self):
        sms_config = self.env['sms.integration'].search([('state', '=', 'done')])
        ''' Sends post request to get session Id against username & password '''

        customer_id = urllib.parse.unquote(sms_config.customer_id).encode('utf8')
        number = urllib.parse.unquote(self.mobile_no).encode('utf8')
        password = urllib.parse.unquote(sms_config.password).encode('utf8')
        message = urllib.parse.quote(self.message_body).encode('utf8')
        mask = urllib.parse.unquote(sms_config.mask).encode('utf8')
        message_type = urllib.parse.unquote(sms_config.message_type).encode('utf8')
        url_api = urllib.parse.unquote(sms_config.url_api).encode('utf8')
        type = sms_config.provider
        repsonse = False
        if type == 'ufone':
            url = (url_api % (
                customer_id, message, mask, number, password, message_type))
            repsonse = requests.get(url, verify=False)
            result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
            if "Successfull" in result:
                self.write({'state': 'sent', 'reason': result})
            else:
                self.write({'state': 'sent', 'reason': result})
            return result
        elif type == 'jazz':
            url = (
                    url_api % (
                customer_id, password, mask, number, message))
            repsonse = requests.get(url, verify=False)
        if repsonse.text == 'Message Sent Successfully!':
            self.write({'state': 'sent', 'reason': repsonse.text})
        else:
            self.write({'state': 'fail', 'reason': repsonse.text})


    def sendMessage(self, number, message, record_id):
        sms_config = self.env['sms.integration'].search([('state', '=', 'done')])
        ''' Sends post request to get session Id against username & password '''

        customer_id = urllib.parse.unquote(sms_config.customer_id).encode('utf8')
        number = urllib.parse.unquote(number).encode('utf8')
        password = urllib.parse.unquote(sms_config.password).encode('utf8')
        message = urllib.parse.quote(message).encode('utf8')
        mask = urllib.parse.unquote(sms_config.mask).encode('utf8')
        message_type = urllib.parse.unquote(sms_config.message_type).encode('utf8')
        url_api = urllib.parse.unquote(sms_config.url_api).encode('utf8')
        type = sms_config.provider
        repsonse = False
        if type == 'ufone':
            url = (url_api % (
                customer_id, message, mask, number, password, message_type))
            repsonse = requests.get(url, verify=False)
            result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
            if "Successfull" in result:
                self.write({'state': 'sent', 'reason': result})
                self.set_sms_status(record_id, result)
            else:
                self.write({'state': 'sent', 'reason': result})
                self.set_sms_status(record_id, result)
            return result
        elif type == 'jazz':
            url = (
                    url_api % (
                customer_id, password, mask, number, message))
            repsonse = requests.get(url, verify=False)
            if repsonse.text == 'Message Sent Successfully!':
                self.write({'state': 'sent', 'reason': repsonse.text})
            else:
                self.write({'state': 'fail', 'reason': repsonse.text})
            self.set_sms_status(record_id, repsonse.text)

    def auto_send_message(self):
        messages = self.env['oc.sms'].search([('state', '=', 'sending')])
        for message in messages:
            print(">>>>>>>>>>>>>>>>>>>>>>> Sending Message >>>>>>>>>>>>>>>>>>>>>>>>>")
            message.sendMessage(message.mobile_no, message.message_body,message.record_id)

    def set_sms_status(self, record_id, result):
        task = self.env['helpdesk.ticket'].search([('id', '=', record_id)])
        task.write({'sms_status': result})
        return True

class HelpDestTicketF(models.Model):
    _inherit = 'helpdesk.ticket'

    techContact = fields.Char('Contact', store=True, size=11)
    sms = fields.Text('SMS', store=True)
    count = fields.Char('Count', store=True, readonly=True, compute='_count')
    sms_status = fields.Char('SMS Status')

    @api.depends('sms')
    def _count(self):
        for rec in self:
            if rec.sms:
                rec.count = len(rec.sms)

    def details(self):
        self.techContact = self.partner_id.phone
        self.sms = str(self.id) + "\n" + str(self.partner_id.cs_number) + "\n" + str(self.name) + "\n" + str(
            self.partner_id.street) + "\n" + str(self.partner_id.street2) + "\n" + str(self.partner_id.city)
        return {
            'warning': {
                'title': "Something bad happened",
                'message': "It was very bad indeed",
            }
        }

    def smsSent(self):
        self.sms_status = "Added in queue"
        vals = {
            'mobile_no': self.techContact,
            'message_body': self.sms,
            'state': 'sending',
            'record_id': self.id
        }
        self.env['oc.sms'].create(vals)
