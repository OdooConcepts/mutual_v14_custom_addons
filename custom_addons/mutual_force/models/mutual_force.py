from datetime import date,datetime,timedelta
from dateutil.relativedelta import *
import datetime as dti
from odoo import api, fields, models, _, SUPERUSER_ID

class force_details(models.Model):
    _name = "force.details"
    _rec_name = 'force_code'

    force_name = fields.Char('Force Name', store=True, required=True)
    supervisor = fields.Char('Supervisor', store=True, required=True)
    contact = fields.Char('Contact#1', store=True, size=12)
    contact2 = fields.Char('Contact#2', store=True, size=12)
    covered_area = fields.Char('Covered Area', store=True, required=True)
    force_code = fields.Char('Force Code', store=True, required=True)


class guard_details(models.Model):
    _name = "guard.details"
    _rec_name = 'guard_name'

    guard_name = fields.Char('Guard Name', store=True, required=True)
    nic = fields.Char('NIC', store=True, required=True)
    contact = fields.Char('Contact', store=True, required=True, size=12)
    address = fields.Char('Address', store=True, required=True)
    force_details = fields.Many2one('force.details', 'Force Name', store=True, track_visibility='onchange')


class BankCustomers(models.Model):
    _name = "bank.customers"
    _rec_name = 'cs'

    name = fields.Char('Name', store=True, track_visibility='onchange')
    cs = fields.Char('CS Number', store=True, track_visibility='onchange')
    bank_coder = fields.Char('Bank Code', store=True, track_visibility='onchange')
    branch_code = fields.Char('Branch Code', store=True, track_visibility='onchange')
    street1 = fields.Char('Address', store=True, track_visibility='onchange')
    street2 = fields.Char('Location', store=True, track_visibility='onchange')
    city = fields.Char('City', store=True, track_visibility='onchange')

class response_time(models.Model):
    _name = "response.time"

    customer = fields.Many2one('bank.customers', 'Customer', store=True)
    name = fields.Char(related='customer.name', store=True, string='Name')
    address = fields.Char(related='customer.street1', store=True, string='Address')
    branch_code = fields.Char(related='customer.branch_code', store=True, string='CS')
    force_name = fields.Char('Force Name', store=True, track_visibility='onchange')
    dispatch_time = fields.Datetime('Dispatch', store=True)
    reach_time = fields.Datetime('Reach', store=True)
    minutes = fields.Char('Minutes', store=True, compute='time_diff')
    move = fields.Datetime('Move', store=True)
    remarks = fields.Char('Remarks', store=True)
    cms = fields.Char('Responsible', store=True)
    shift_time = fields.Char('Shift', store=True)

    @api.depends('dispatch_time','reach_time')
    def time_diff(self):
        if self.dispatch_time and self.reach_time:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            dispatch = datetime.strptime(str(self.dispatch_time), date_format)
            reach = datetime.strptime(str(self.reach_time), date_format)
            # find the difference between two dates
            diff = reach - dispatch
            self.minutes = diff
            self.shift_assign()


    def shift_assign(self):
        self.env.cr.execute("select * from response_time where shift_time is null and reach_time is not null")
        all_visit = self.env.cr.dictfetchall()
        if len(all_visit) != 0:
            for v in all_visit:
                dt = (dti.datetime.strptime(str(v['reach_time']), '%Y-%m-%d %H:%M:%S')+timedelta(hours=5)).time()
                if dt >= dti.time(8,1,0,0) and dt <= dti.time(16,0,59,0):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"morning"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif (dt >= dti.time(16,1,0,0)) and (dt <= dti.time(23,30,59,0)):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"evening"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif ((dt >= dti.time(23,31,0,0) and dt <= dti.time(23,59,59,0))):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"night"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif ((dt >= dti.time(0,0,0,0) and dt <= dti.time(8,0,59,0))):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"night"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")





class NewVisits(models.Model):
    _name = "new.visits"

    name = fields.Char('Customer Name', store=True, track_visibility='onchange')
    cs_number = fields.Char('CS Number', store=True)
    address = fields.Char('Address', store=True)
    stages = fields.Many2one('new.visits.stages', 'Stage', store=True)
    first_visit = fields.Datetime('First Visit', store=True)
    second_visit = fields.Datetime('Second Visit', store=True)
    first_visit_remarks = fields.Text('First Visit Remarks', store=True)
    second_visit_remarks = fields.Text('Second Visit Remarks', store=True)


    @api.model
    def show_all_stages(self):
        stages = self.env['new.visits.stages'].search([]).name_get()
        return stages, None

    _group_by_full = {
        'stages': show_all_stages,
    }


class NewVisitsStages(models.Model):
    _name = "new.visits.stages"

    name = fields.Char('Stage Name',store=True,track_visibility='onchange')


class RecoveryVisits(models.Model):
    _name = "recovery.visits"

    cs_number = fields.Many2one('bank.customers', 'Customer', store=True)
    name = fields.Char(size=12, string='Name', related='cs_number.name', store=True)
    force = fields.Char('Force', store=True, required=True)
    time = fields.Datetime('Time', store=True)
    status = fields.Char('Status', store=True)
    recovery_officer = fields.Char('Recovery Officer', store=True, required=True)


class ResPartnerInherit(models.Model):

    _inherit = "res.partner"

    is_visit = fields.Boolean('Is Force Visit Required?', store=True)

    @api.onchange('is_visit','street')
    def create_new_visit(self):
        if self.name!=False:
            stage = self.env['new.visits.stages'].search([['name', '=', 'New'], ])
            if self.is_visit == True:
                self.env['new.visits'].create({
                    'name': self.name,
                    'cs_number': self.cs_number,
                    'address': (str(self.street) + ' ' +str(self.street2)+' '+str(self.city)).replace('False',' '),
                    'stages': stage.id
                })
                self.env['bank.customers'].create({
                    'name': self.name,
                    'cs': self.cs_number,
                    'street1': str(self.street).replace('False',' '),
                    'street2': str(self.street2).replace('False',' '),
                    'city': str(self.city).replace('False',' ')
                })

