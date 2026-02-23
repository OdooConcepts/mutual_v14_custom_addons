# The file name of this file must match the filename name which we import in __init__.py file
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
import requests


class inheritStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    code = fields.Char('Short Name', required=True, size=50, help="Short name used to identify your warehouse")

# ======================================== Project.task class implementation Begins =====================================


class MutualProjects(models.Model):
    _inherit = "project.task"

    remark_by_cms = fields.Text('Remarks By CMS', store=True)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    sale_order_task = fields.Many2one('sale.order', 'Sale Order', store=True)
    reviewer_id = fields.Many2one('res.users', 'Forwarded to', domain="[('is_technician','=',False)]", tracking=True)
    user_id = fields.Many2one('res.users', 'Assigned Tech', domain="[('is_technician','=',True)]", tracking=True)
    city_task = fields.Char(related='partner_id.city', string='City', readonly=True, store=True)
    branch_code_task = fields.Char(related='partner_id.branch_code', string='Branch Code', readonly=True, store=True)
    bank_code_task = fields.Char(related='partner_id.bank_code', string='Bank Code', readonly=True, store=True)
    monitoring_address_task = fields.Char(related='partner_id.street', string='Monitoring address', readonly=True,
                                          store=True)
    cs_number_task = fields.Char(related='partner_id.cs_number', string='CS Number', readonly=True, store=True)
    tech_name_tasks = fields.One2many('tech.activities.tasks', 'tech_name_tasks', string='Timesheets', store=True)
    complaint_reference = fields.Integer('Complaint Reference', store=True)
    time_in = fields.Datetime('Time In', store=True, copy=False, index=True)
    time_out = fields.Datetime('Time Out', store=True, copy=False, index=True)
    compute_total_time = fields.Char('Total Time', store=True, readonly=True, compute='_compute_total_time')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Most Urgent')],
        'Priority', store=True, index=True)
    first_signal_time_task = fields.Datetime('First Signal Time', store=True, copy=True, index=True)
    name = fields.Selection([
        ('Uplink', 'Uplink'),
        ('Survey', 'Survey'),
        ('Disco', 'Disco'),
        ('Additional', 'Additional'),
        ('Shifting', 'Shifting'),
        ('Reconnection', 'Reconnection'),
        ('NewInstallation', 'New Installation')],
        'Task', required=True, store=True, index=True)

    @api.depends('time_in', 'time_out')
    def _compute_total_time(self):
        for record in self:
            if record.time_in and record.time_out:
                time_in = record.time_in
                time_in_hr = int(time_in[11:13]) + 5
                time_in_min = int(time_in[14:16])
                time_in_sec = int(time_in[17:19])
                time_out = record.time_out
                time_out_hr = int(time_out[11:13]) + 5
                time_out_min = int(time_out[14:16])
                time_out_sec = int(time_out[17:19])
                total_hr = time_out_hr - time_in_hr
                total_min = abs(time_out_min - time_in_min)
                total_sec = abs(time_out_sec - time_in_sec)
                record.compute_total_time = f"{total_hr}:{total_min}:{total_sec}"


# ======================================== Project.Issue class implementation Begins =====================================

class ProjectIssue(models.Model):
    _inherit = "helpdesk.ticket"

    task_id = fields.Many2one('project.task', ' ', domain="[('project_id','=',project_id)]")
    system_status = fields.Char('System Status', store=True)
    # stage_id = fields.Many2one('project.task.type', 'Stage', select=True)
    complaint_status = fields.Char('Complaint Status', store=True)
    sale_order_issue = fields.Many2one('sale.order', 'Sale Order', store=True)
    contact = fields.Char('Contact', related='user_id.mobile', readonly=True)
    customer = fields.Char('Customer', related='partner_id.name', readonly=True)
    bm_number_issue = fields.Char('BM Number Issue', related='partner_id.office', readonly=True)
    om_number_issue = fields.Char('OM Number Issue', related='partner_id.phone', readonly=True)
    mobile_logged = fields.Char('Mobile Logged', related='create_uid.mobile', readonly=True)
    sms = fields.Text('SMS', store=True)
    cs_number_issue = fields.Char('CS Number', related='partner_id.cs_number', readonly=True)
    city_issue = fields.Char('City', related='partner_id.city', readonly=True)
    branch_code_issue = fields.Char('Branch Code', related='partner_id.branch_code', readonly=True)
    bank_code_issue = fields.Char('Bank Code', related='partner_id.bank_code', readonly=True)
    monitoring_address_issue = fields.Char('Bank Address', related='partner_id.street', readonly=True)
    remark_by_cms = fields.Text('Remarks By CMS', store=True)
    complaint_source = fields.Selection(
        [("By Anwar Zaib", "By Anwar Zaib"), ("Complaint generated by LSR", "By LSR"), ("By Email", "By Email"),
         ("By CMS", "By CMS"), ("Direct", "Direct")], 'Complaint Source', required=True)
    courtesy_remarks = fields.One2many('courtesy.remarks', 'complaint_title', 'Courtesy Remarks', store=True)
    cms_remarks = fields.One2many('cms.remarks', 'complaint_title', 'CMS Remarks', store=True)
    bank_remarks = fields.One2many('bank.remarks', 'complaint_title', 'Bank Remarks', store=True)
    tech_name = fields.One2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True)
    user_id_issue = fields.Many2one('res.users', 'Forwarded to', required=False, select=True,
                                    domain="[('is_technician','=',False)]")
    user_id = fields.Many2one('res.users', 'Assigned Technician', required=False, select=True,
                              domain="[('is_technician','=',True)]")
    compute_total_time = fields.Char('Total Time', store=True, readonly=True, compute='_compute_total_time')
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]")
    categ_ids = fields.Many2many('project.category', string='Other Complaints')
    date_start = fields.Datetime('Time In', select=True, copy=True)
    date_end = fields.Datetime('Time Out', select=True, copy=True)
    first_signal_time = fields.Datetime('First Signal Time', select=True, copy=True)
    priority = fields.Selection([('0', 'Normal'), ('1', 'Urgent'), ('2', 'Most Urgent')], 'Priority', select=True,
                                store=True)
    name =  fields.Selection([("Activation & Deactivation Problem	(I)", "Activation & Deactivation Problem (I)"),
                                  ("ADDITONAL WORK IN PENDING	(I)", "ADDITONAL WORK IN PENDING	(I)"),
                                  ("ALL PANIC CHECK (I)", "ALL PANIC CHECK	(I)"),
                                  ("All Zone Check (I)", "All Zone Check (I)"),
                                  ("BAS Shifting Case with Date of Shifting Urgent (I)",
                                   "BAS Shifting Case with Date of Shifting Urgent (I)"),
                                  ("BATTERY INSTALL (I)", "BATTERY INSTALL	(I)"),
                                  ("Battery Problem (I)", "Battery Problem	(I)"),
                                  ("Baypass Zone (I)", "Baypass Zone (I)"),
                                  ("BENTAL PROBLEM (I)", "BENTAL PROBLEM (I)"),
                                  ("BRANCH  CLOSED (I)", "BRANCH CLOSED (I)"),
                                  ("BRANCH SHIFT (I)", "BRANCH SHIFT (I)"),
                                  ("BRANCH UNDER RENOVATION (I)", "BRANCH UNDER RENOVATION (I)"),
                                  ("BUGLARY ALARM PROBLEM	(I)", "BUGLARY ALARM PROBLEM	(I)"),
                                  ("CALL LATER (I)", "CALL LATER (I)"),
                                  ("Cancel(I)", "Cancel (I)"),
                                  ("Change Keypad Code (I)", "Change Keypad Code(I)"),
                                  ("Change PTCL Line (I)", "Change PTCL Line (I)"),
                                  ("change the location (I)", "change the location (I)"),
                                  ("CLOSING SIGNAL PROBLEM (I)", "CLOSING SIGNAL PROBLEM (I)"),
                                  ("Code Dailer Problem (I)", "Code Dailer Problem	(I)"),
                                  ("Connect PTCL Line	(I)", "Connect PTCL Line(I)"),
                                  ("Delay Time Problem (I)", "Delay Time Problem (I)"),
                                  ("DEVICES INSTALL (I)", "DEVICES INSTALL	(I)"),
                                  ("DEVICES RE-INSTALL (I)", "DEVICES RE-INSTALL	(I)"),
                                  ("Disable Zone	(I)", "	Disable Zone(I)"),
                                  ("Electricity Problem(I)", "Electricity Problem(I)"),
                                  ("False Alarming (I)", "False Alarming (I)"),
                                  ("Fire Alarm Problem (I)", "Fire Alarm Problem (I)"),
                                  ("SIM balance issue	(I)", "SIM balance issue	(I)"),
                                  ("GSM Problem	(I)", "GSM Problem	(I)"),
                                  ("GSM SIM INSTALL (I)", "GSM SIM INSTALL	(I)"),
                                  ("Gsm Sim N/A (I)", "Gsm Sim N/A (I)"),
                                  ("Guard less Activation	(I)", "Guard less Activation (I)"),
                                  ("HEAVY METAL PROBLEM (I)", "HEAVY METAL PROBLEM	(I)"),
                                  ("hooter install (I)", "hooter install (I)"),
                                  ("Hooter Problem (I)", "Hooter Problem(I)"),
                                  ("Hooter Wire Connect (I)", "Hooter Wire Connect	(I)"),
                                  ("install keypad (I)", "	install keypad	(I)"),
                                  ("Keypad Beeping (I)", "	Keypad Beeping	(I)"),
                                  ("Keypad Code Problem (I)", "Keypad Code Problem (I)"),
                                  ("KEYPAD DEAD (I)", "KEYPAD DEAD(I)"),
                                  ("Keypad Hang (I)", "Keypad Hang(I)"),
                                  ("KEYPAD INSTALL (I)", "KEYPAD INSTALL (I)"),
                                  ("Keypad Problem (I)", "Keypad Problem (I)"),
                                  ("KEYPAD SHIFTING (I)", "KEYPAD SHIFTING (I)"),
                                  ("Late Transmission Problem (I)", "Late Transmission Problem (I)"),
                                  ("Most Urgent Complain (I)", "Most Urgent Complain (I)"),
                                  ("NO RESPONSE (I)", "NO RESPONSE	(I)"),
                                  ("ok (I)", "	ok (I)"),
                                  ("Other (I)", "Other (I)"),
                                  ("Open/Close Problem (I)", "	Open/Close Problem (I)"),
                                  ("PANIC BUTTON DAMAGED (I)", "PANIC BUTTON DAMAGED (I)"),
                                  ("Panic Not Working	(I)", "Panic Not Working (I)"),
                                  ("PCB KIT FAULTY (I)", "PCB KIT FAULTY (I)"),
                                  ("Penal Beeping	(I)", "Penal Beeping (I)"),
                                  ("PENAL LOCATION CHANGE	(I)", "PENAL LOCATION CHANGE	(I)"),
                                  ("Penal Problem (I)", "Penal Problem (I)"),
                                  ("PIR Problem (I)", "PIR Problem (I)"),
                                  ("Programming Error Urgent Check (I)", "Programming Error Urgent Check (I)"),
                                  ("Ptcl Change (I)", "Ptcl Change (I)"),
                                  ("Ptcl Connect (I)", "Ptcl Connect (I)"),
                                  ("PTCL LINE DEAD (I)", "PTCL LINE DEAD (I)"),
                                  ("PTCL LINE DISTORTION (I)", "PTCL LINE DISTORTION (I)"),
                                  ("PTCL N/A (I)", "PTCL N/A (I)"),
                                  ("PTCL Problem due to System (I)", "PTCL Problem due to System (I)"),
                                  ("R/S Problem	(I)", "	R/S Problem	(I)"),
                                  ("RE-INSTALLATION OF SYSTEM/DEVICES (I)", "RE-INSTALLATION OF SYSTEM/DEVICES	(I)"),
                                  ("Relocation of O/C	(I)", "Relocation of O/C (I)"),
                                  ("REMOTE PANIC PROBLEM(I)", "REMOTE PANIC PROBLEM (I)"),
                                  ("SD Not Working (I)", "SD Not Working (I)"),
                                  ("SIGNAL ISSUE (I)", "SIGNAL ISSUE (I)"),
                                  ("SIM BALANCE PROBLEM (I)", "	SIM BALANCE PROBLEM	(I)"),
                                  ("SIM BLOCKED (I)", " SIM BLOCKED (I)"),
                                  ("SIM BLOCKED/OUTGOING SERVICE ISSUE (I)", "SIM BLOCKED/OUTGOING SERVICE ISSUE (I)"),
                                  ("SIM INSTALL (I)", "SIM INSTALL (I)"),
                                  ("SMOKE DECTECTOR PROBLEM (I)", "SMOKE DECTECTOR PROBLEM (I)"),
                                  ("SMOOK DETECTOR INSTAL (I)", "SMOOK DETECTOR INSTAL	(I)"),
                                  ("SMS Receiving Problem (I)", "SMS Receiving Problem (I)"),
                                  ("SYSTEM BEEPING (I)", "SYSTEM BEEPING (I)"),
                                  ("SYSTEM BRIEFING REQUIRED (I)", "SYSTEM BRIEFING REQUIRED (I)"),
                                  ("System Dead (I)", "System Dead	(I)"),
                                  ("System Dead urgent (I)", "System Dead urgent(I)"),
                                  ("SYSTEM HANG (I)", "SYSTEM HANG (I)"),
                                  ("System Problem Urgent check (I)", "System Problem Urgent check (I)"),
                                  ("System Remove/Dismentle (I)", "System Remove/Dismentle (I)"),
                                  ("System Remove/Dismentle Case with Date Urgent (I)",
                                   "System Remove/Dismentle Case with Date Urgent (I)"),
                                  ("System Shift(I)", "System Shift(I)"),
                                  ("TECHNICIAN REQUIRED(I)", "TECHNICIAN REQUIRED(I)"),
                                  ("Temper problem(I)", "Temper problem(I)"),
                                  ("Transmission Problem(I)", "Transmission Problem(I)"),
                                  ("Transmission Problem & System Check (I)", "Transmission Problem & System Check(I)"),
                                  ("USER CODE CHANGED	(I)", "USER CODE CHANGED	(I)"),
                                  ("USER CODE PROBLEM	(I)", "USER CODE PROBLEM	(I)"),
                                  ("user code provide	(I)", "user code provide	(I)"),
                                  ("V/S Problem (I)", "V/S Problem	(I)"),
                                  ("Wiring Check (I)", "Wiring Check (I)"),
                                  ("Zone 1 Problem (I)", "Zone 1 Problem (I)"),
                                  ("Zone 2 Problem (I)", "Zone 2 Problem (I)"),
                                  ("Zone 3 Problem (I)", "Zone 3 Problem (I)"),
                                  ("Zone 4 Problem (I)", "Zone 4 Problem (I)"),
                                  ("Zone 5 Problem (I)", "Zone 5 Problem (I)"),
                                  ("Zone 6 Problem (I)", "Zone 6 Problem (I)"),
                                  ("Zone 7 Problem (I)", "Zone 7 Problem (I)"),
                                  ("Zone 8 Problem (I)", "Zone 8 Problem (I)"),
                                  ("Additional(T)", "Additional(T)"),
                                  ("Backup Battery Required(T)", "Backup Battery Required (T)"),
                                  ("BAS Penal/Device Location Change (T)", "BAS Penal/Device Location Change (T)"),
                                  ("Fixed Panic Button Required (T)", "Fixed Panic Button Required (T)"),
                                  ("Foot Panic Paddles Required T", "Foot Panic Paddles Required T"),
                                  ("GSM/Bental Required (T)", "GSM/Bental Required (T)"),
                                  ("H/M (Heavy Metal) Required (T)", "H/M (Heavy Metal) Required (T)"),
                                  ("Hooter Required (T)", "Hooter Required (T)"),
                                  ("Keypad Required (T)", "Keypad Required (T"),
                                  ("O/C (Magnetic Door Contact) Required (T)",
                                   "O/C (Magnetic Door Contact) Required (T)"),
                                  ("PCB Required (T)", "PCB Required (T)"),
                                  ("PIR (Motion Sensor) Required (T)", "PIR (Motion Sensor) Required (T)"),
                                  ("R/S (Roller Shutter) Required (T)", "R/S (Roller Shutter) Required (T)"),
                                  ("Remote/Wireless Panic Required (T)", "Remote/Wireless Panic Required (T)"),
                                  ("Re-Wiring Required (T)", "Re-Wiring Required (T)"),
                                  ("S/D (Smoke Detector) Required (T)", "S/D (Smoke Detector) Required (T)"),
                                  ("System Shifting/Re-installation (T)", "System Shifting/Re-installation (T)"),
                                  ("Transformer Required (T)", "Transformer Required (T)"),
                                  ("V/S (Vibration Sensor) Required (T)", "V/S (Vibration Sensor) Required (T)"),
                                  ("Survey (T)", "Survey (T)"),
                                  ("New Installation (T)", "New Installation (T)"),
                                  ("Disco (T)", "Disco (T)"),
                                  ("Special Task (T)", "Special Task (T)"),
                                  ("UPS connect with BAS", "UPS connect with BAS"),
                                  ("Zone by pass ", "Zone by pass "),
                                  ("ATM upper and cosmetic door connect with BAS",
                                   "ATM upper and cosmetic door connect with BAS")
                                  ],
                                 'Complaint Title', required=True)
    zone1 = fields.Boolean('Zone1', store=True)
    zone2 = fields.Boolean('Zone2', store=True)
    zone3 = fields.Boolean('Zone3', store=True)
    zone4 = fields.Boolean('Zone4', store=True)
    zone5 = fields.Boolean('Zone5', store=True)
    zone6 = fields.Boolean('Zone6', store=True)
    zone7 = fields.Boolean('Zone7', store=True)
    zone8 = fields.Boolean('Zone8', store=True)
    zone9 = fields.Boolean('Zone9', store=True)
    panic = fields.Boolean('Panic', store=True)
    duress = fields.Boolean('Duress', store=True)
    medical = fields.Boolean('Medical', store=True)
    fire = fields.Boolean('Fire', store=True)
    gsm = fields.Selection([('GSM', 'GSM'), ('Bental', 'Bental')], string='GSM/Bental')
    gsm_number = fields.Char('GSM/Bental', store=True)
    gsm_postpaid_prepaid = fields.Selection([('Prepaid', 'Prepaid'), ('Postpaid', 'Postpaid')], 'Prepaid/Postpaid', store=True)
    ptcl = fields.Char('PTCL', store=True)
    ptcl_dedicated_shared = fields.Selection([('Dedicated', 'Dedicated'), ('Shared', 'Shared')], 'Dedicated/Shared', store=True)
    response_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], 'Response check', store=True)
    status = fields.Char('Final Status', store=True)
    complaint_log_bank = fields.Char('Complaint Log By Client', size=25, store=True)
    check_by = fields.Char('Check By Client', size=25, store=True)
    courtesy = fields.Text('Courtesy Remarks', store=True)
    clientname = fields.Char('Client Name', store=True, size=30, required=True)
    check = fields.Char('Type', store=True, compute='type')
    convert_to_task = fields.Boolean('Convert to Task', store=True)
    tech = fields.Char('Assigned to Technician', store=True, compute='assign_tech'),
    technician_name = fields.Many2one('hr.employee', 'Technician Name', required=False, track_visibility='onchange', domain="[('department_id','=','Technician')]")
    techContact = fields.Char('Contact', store=True, size=11, readonly=False, compute='get_contact')
    count = fields.Char('Count', store=True, readonly=True, compute='_count')
    #restrict = fields.Char('Restrict', store=True, readonly=True, compute='restrictAssignedtoTech')
    pending = fields.Boolean('Pending', store=True, groups='project.group_project_manager')
    sms_status = fields.Char('SMS Status')
    # date_action_last = fields.Datetime('Last Action Date', readonly=True, select=True, store=True)

    def details(self):
        if (self.partner_id.is_company == False):
            self.sms = str(
                self.id) + "\n" + self.name + "\n" + self.cs_number_issue + "\n" + self.monitoring_address_issue + "\n" + self.city_issue

        elif self.cs_number_issue and self.bank_code_issue and self.branch_code_issue and self.monitoring_address_issue and self.city_issue and self.description:
            self.sms = str(self.id) + "\n" + self.name + "\n" + self.description + "\n" + \
                       self.bank_code_issue + "\n" + self.cs_number_issue + "\n" + "BC" + self.branch_code_issue + "\n" + self.monitoring_address_issue + "\n" + self.city_issue

        elif self.cs_number_issue and self.bank_code_issue and self.branch_code_issue and self.monitoring_address_issue and self.city_issue:
            self.sms = str(self.id) + "\n" + self.name + "\n" + \
                       self.bank_code_issue + "\n" + self.cs_number_issue + "\n" + "BC" + self.branch_code_issue + "\n" + self.monitoring_address_issue + "\n" + self.city_issue
        else:
            raise ValidationError('Information Incomplete', 'You must have full information before sending an SMS')
    def smsSent(self):
        if self.number:
            if self.number and self.sms:
                ''' Sends post request to get session Id against username & password '''
                sms_carrier = self.env['ir.config_parameter'].sudo().get_param('sms_carrier')
                number = urllib.unquote(self.number).encode('utf8')
                message = urllib.quote((self.sms).encode("utf-8"))
                if int(self.count):
                    if sms_carrier == 'UFONE':
                        url = (
                                "https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=03315506614&message=%s&shortcode=MUTUAL&lang=English&mobilenum=%s&password=Ptml@123456&groupname=&messagetype=Transactional" % (
                            message, number))
                        repsonse = requests.get(url, verify=False)
                        result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[
                            0].data
                        self.sms_status = result
                        # self.env['sms.report'].create(
                        #     {'to': number, 'sms': self.sms, 'status': result, 'type': 'RSO Message'})
                        return result
                    elif sms_carrier == 'JAZZ':
                        url = (
                                "https://connect.jazzcmt.com/sendsms_url.html?Username=03051912864&Password=IPzxs890d&From=MUTUAL&To=%s&Message=%s" % (
                            number, message))
                        repsonse = requests.get(url, verify=False)
                        if repsonse.text == 'Message Sent Successfully!':
                            self.sms_status = repsonse.text
                        else:
                            self.sms_status = repsonse.text
                        # self.env['sms.report'].create(
                        #         {'to': number, 'sms': self.sms, 'status': repsonse.text, 'type': 'RSO Message'})
                else:
                    raise ValidationError('Limit Exceed \n SMS must be within 160 characters')
        else:
            raise ValidationError('Empty Field \n Kindly enter mobile number of technician')

    @api.depends('tech_name.technician_name')
    def assign_tech(self):
        for rec in self:
            technician = ''
            for technicians in rec.tech_name:
                technician += str(technicians.technician_name.name) + ' '
            rec.tech = technician

    @api.depends('name')
    def type(self):
        for rec in self:
            str = rec.name
            if str:
                if str.find('(I)') != -1:
                    rec.check = "Issue"
                elif str.find('(T)') != -1:
                    rec.check = "Task"

    @api.depends('sms')
    def _count(self):
        for rec in self:
            if rec.sms:
                rec.count = len(rec.sms)

    @api.depends('tech_name.technician_name')
    def assign_tech(self):
        technician = ''
        for technicians in self.tech_name:
            technician += str(technicians.technician_name.name) + ' '
        self.tech = technician

    @api.depends('technician_name')
    def get_contact(self):
        for rec in self:
            rec.techContact = rec.technician_name.work_phone
    
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for record in self:
            if record.date_start and record.date_end:
                date_start = fields.Datetime.from_string(record.date_start)
                date_end = fields.Datetime.from_string(record.date_end)
                total_time = date_end - date_start
                record.compute_total_time = str(total_time)
            else:
                record.compute_total_time = "Not Started"
    
#    @api.model
#    def create(self, vals):
#        rec = super(ProjectIssue, self).create(vals)
#        stage_ids = self.env['helpdesk.stage'].sudo().search([('is_close','=',True)]).ids
#        if self.search_count([('partner_id','=',rec.partner_id.id),('stage_id','not in',stage_ids)])>1:
#            raise ValidationError("A new complaint cannot be created for this customer as there is #already an unresolved complaint."
#                                  "\n Please resolve the pending complaint first.")
#        return rec

#    def write(self, vals):
#        if self.stage_id.is_close:
#            raise ValidationError("You cannot modify stage of resolved complaint")
#        res = super(ProjectIssue, self).write(vals)
#        return res

    def unlink(self):
        for record in self:
            if record.stage_id and record.stage_id.name.lower() in ['done', 'cancelled']:
                raise ValidationError("Cannot delete issues that are done or cancelled.")
        return super(ProjectIssue, self).unlink()

    def open_issue_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': self.id,
            'target': 'current',
        }


class TechActivitiesIssues(models.Model):
    _name = "tech.activities.issues"
    _description = "Tech Activities Issues"

    bas = fields.Selection([
        ('GSM Only', 'GSM Only'),
        ('Bentel Only', 'Bentel Only'),
        ('PTCL Only', 'PTCL Only'),
        ('Bentel and PTCL', 'Bentel and PTCL'),
        ('GSM and PTCL', 'GSM and PTCL'),
        ('Nil', 'Nil')],
        string='BAS Connected To', store=True)

    sim_status = fields.Selection([
        ('Postpaid', 'Postpaid'),
        ('Prepaid', 'Prepaid'),
        ('Inactive', 'Inactive'),
        ('Not Available', 'Not Available'),
        ('Nil', 'Nil')],
        string='Sim Status', store=True)

    pending = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Nil', 'Nil')],
        string='Work is Pending', store=True)

    tech_name = fields.Many2one('helpdesk.ticket', string='Complaint Title')

    technician_name = fields.Many2one('hr.employee', string='Technician Name', required=True, tracking=True,
                                      domain="[('department_id','=','Technician')]", default='')

    reason = fields.Char('Final Status', store=True)

    systemstatus = fields.Char('System Status', store=True)

    total_time = fields.Float('Total Time', store=True)

    date = fields.Date('Date', store=True)

    compute_total_time = fields.Char('T/T', store=True, readonly=True, compute='_compute_total_time')

    first_signal = fields.Datetime('F/T', copy=True, store=True)

    date_start = fields.Datetime('T/I', copy=True, store=True)

    date_end = fields.Datetime('T/O', copy=True, store=True)

    cs_number = fields.Char('CS Number', related='tech_name.cs_number_issue', readonly=True)

    bank_code = fields.Char('Bank Code', related='tech_name.bank_code_issue', readonly=True)

    complaint_source = fields.Selection('Complaint Source', related='tech_name.complaint_source', readonly=True)

    monitoring_address_issue = fields.Char('Address', related='tech_name.monitoring_address_issue', readonly=True)

    issue_id = fields.Integer('Complaint ID', related='tech_name.id', readonly=True)

    branch_code = fields.Char('Branch Code', related='tech_name.branch_code_issue', readonly=True)

    multi_tech = fields.Many2many('hr.employee', string='Other Tech',
                                  domain="[('department_id','=','Technician')]")

    status = fields.Selection([
        ('Time In/Out', 'Time In/Out'),
        ('Resolved', 'Resolved'),
        ('Under Process', 'Under Process'),
        ('Issue at bank end', 'Issue at bank end'),
        ('Additional/Device Replacement', 'Additional/Device Replacement'),
        ('Assigned to Technician', 'Assigned to Technician'),
        ('Complaints/Tasks', 'Complaints/Tasks'),
        ('Online Resolved', 'Online Resolved'),
        ('Inventory Check', 'Inventory Check')],
        string='Complaint Marking', store=True)

    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for record in self:
            if record.date_start and record.date_end:
                date_format = "%Y-%m-%d %H:%M:%S"
                time_in = datetime.strptime(str(record.date_start), date_format)
                time_out = datetime.strptime(str(record.date_end), date_format)
                diff = time_out - time_in
                record.compute_total_time = str(diff)
            else:
                record.compute_total_time = "Not Started"

    @api.model
    def create(self, vals):
        rec = super(TechActivitiesIssues, self).create(vals)
        if rec.bas == 'Nil':
            raise ValidationError(
                "You cannot mark 'Nil' in BAS Connected status")
        return rec

    def write(self, vals):
        if self.status =='Resolved' or self.status == 'Online Resolved':
            raise ValidationError("You cannot modify stage of resolved complaint")
        res = super(TechActivitiesIssues, self).write(vals)
        if self.bas == 'Nil':
            raise ValidationError(
                "You cannot mark 'Nil' in BAS Connected status")
        return res

    @api.onchange('status')
    def changestatus(self):
        if self.status:
            stage_id_map = {
                "Resolved": 15,
                "Time In/Out": 17,
                "Under Process": 21,
                "Assigned to Technician": 2,
                "Additional/Device Replacement": 20,
                "Issue at bank end": 22,
                "Inventory Check": 18,
                "Online Resolved": 4
            }
            if self.status in stage_id_map:
                self.env.cr.execute(
                    'UPDATE helpdesk_ticket SET stage_id = %s WHERE id = %s' % (stage_id_map[self.status], self.tech_name.id)
                )
            else:
                raise ValidationError('You do not have rights to move this card into this bucket')


class LowMessages(models.Model):
    _name = "low.messages"
    _description = "Low Messages"

    count = fields.Char('Count', store=True, readonly=True, compute='_count')
    bank = fields.Many2one('res.partner', string='Customer', store=True, required=True)
    employee_name = fields.Many2one('hr.employee', string='Technician Name',
                                    domain="[('department_id','=','Technician')]", default='',
                                    oldname='technician_name')
    cs = fields.Char('CS Number', store=True, readonly=True)
    branch_code = fields.Char('Branch Code', store=True, readonly=True)
    address = fields.Text('Address', store=True, readonly=True)
    sms = fields.Text('SMS', store=True,
                      default='Backup Battery is running low due to long electric failures. Please recharge it within 1.5hr for smooth working of system(MSS 111-238-222)')
    number = fields.Char('Contact Number', store=True, size=11, required=True)
    technician = fields.Boolean('Technician', store=True)
    rso_sms = fields.Boolean('RSO', store=True)
    sms_status = fields.Char('SMS Status')

    @api.depends('sms')
    def _count(self):
        for record in self:
            record.count = str(len(record.sms)) if record.sms else '0'

    @api.onchange('bank')
    def customer_details(self):
        if not self.technician and self.bank:
            self.cs = self.bank.cs_number
            self.branch_code = self.bank.branch_code
            self.address = "\n".join(filter(None, [self.bank.street, self.bank.street2, self.bank.city]))

    @api.onchange('employee_name')
    def technician_contact(self):
        if self.technician and self.employee_name:
            self.number = self.employee_name.work_phone

    def smsSent(self):
        if self.number and self.sms:
            sms_carrier = self.env['ir.config_parameter'].sudo().get_param('sms_carrier')
            number = self.number
            message = self.sms
            if len(message) <= 160:
                if sms_carrier == 'UFONE':
                    url = (
                        f"https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=03315506614&message={message}&shortcode=MUTUAL&lang=English&mobilenum={number}&password=Ptml@123456&groupname=&messagetype=Transactional"
                    )
                    response = requests.get(url, verify=False)
                    result = parseString(response.content).getElementsByTagName('response_text')[0].childNodes[0].data
                    self.sms_status = result
                elif sms_carrier == 'JAZZ':
                    url = (
                        f"https://connect.jazzcmt.com/sendsms_url.html?Username=03051912864&Password=IPzxs890d&From=MUTUAL&To={number}&Message={message}"
                    )
                    response = requests.get(url, verify=False)
                    self.sms_status = response.text
            else:
                raise ValidationError('Limit Exceed', 'SMS must be within 160 characters')
        else:
            raise ValidationError('Empty Field', 'Kindly enter the mobile number of the technician')

class TechActivitiesTasks(models.Model):
    _name = "tech.activities.tasks"
    _description = "Tech Activities Tasks"
    _order = "date_start desc"

    systemstatus = fields.Char('System Status', size=100, store=True)
    tech_name_tasks = fields.Many2one('project.task', string='Task Title')
    technician_name_tasks = fields.Many2one('hr.employee', string='Technician Name',
                                            domain="[('department_id.name','=','Technician')]")
    reason_tasks = fields.Char('Final Status', size=100, store=True)
    total_time_tasks = fields.Float('Total Time', store=True)
    date_tasks = fields.Date('Date', store=True)
    compute_total_time = fields.Char('T/T', store=True, readonly=True, compute='_compute_total_time')
    first_signal = fields.Datetime('F/T', copy=True, write=['project.group_project_manager'],
                                   read=['project.group_project_user'])
    date_start = fields.Datetime('T/I', copy=True, write=['project.group_project_manager'],
                                 read=['project.group_project_user'])
    date_end = fields.Datetime('T/O', copy=True, write=['project.group_project_manager'],
                               read=['project.group_project_user'])
    cs_number = fields.Char(related='tech_name_tasks.cs_number_task', string='CS Number')
    task_id = fields.Integer(related='tech_name_tasks.id', string='Task ID')
    complaint_reference = fields.Integer(related='tech_name_tasks.complaint_reference', string='Complaint Reference')
    branch_code = fields.Char(related='tech_name_tasks.branch_code_task', string='Branch Code')
    multi_tech = fields.Many2many('hr.employee', string='Other Tech',
                                  domain="[('department_id.name','=','Technician')]")

    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for record in self:
            if record.date_start and record.date_end:
                date_format = "%Y-%m-%d %H:%M:%S"
                time_in = datetime.strptime(record.date_start, date_format)
                time_out = datetime.strptime(record.date_end, date_format)
                diff = time_out - time_in
                record.compute_total_time = str(diff)


class ComplaintMessages(models.Model):
    _name = "complaint.messages"
    _description = "Complaint Messages"

    message = fields.Text('Message', store=True)
    receiver_contact = fields.Char('Receiver Contact', store=True)
    status = fields.Char('Status', store=True, default='0')
    receiver_name = fields.Char('Receiver Name', store=True)
    sender_name = fields.Char('Sender', store=True)
    date_now = fields.Date('Date', store=True)


class GuardTracking(models.Model):
    _name = "guard.tracking"
    _description = "Guard Tracking"

    card_no = fields.Char('RF_ID', store=True)
    customer = fields.Many2one('res.partner', 'Customer', store=True)
    branch_code = fields.Char(related='customer.branch_code', string='Branch Code', store=True)


class CourtesyRemarks(models.Model):
    _name = "courtesy.remarks"
    _description = "Courtesy Remarks"

    complaint_title = fields.Many2one('helpdesk.ticket', 'Complaint Title')
    remarks = fields.Char('Remarks', store=True, required=True)


class CmsRemarks(models.Model):
    _name = "cms.remarks"
    _description = "CMS Remarks"

    complaint_title = fields.Many2one('helpdesk.ticket', 'Complaint Title')
    remarks = fields.Char('Remarks', store=True)
    client_name = fields.Char('Client', store=True)
    responsible_person = fields.Char('Responsible Person', store=True)


class BankRemarks(models.Model):
    _name = "bank.remarks"
    _description = "Bank Remarks"

    complaint_title = fields.Many2one('helpdesk.ticket', 'Complaint Title')
    remarks = fields.Char('Remarks', store=True)
    client_name = fields.Char('Client', store=True)
    responsible_person = fields.Char('Responsible Person', store=True)


class OldTimeInOut(models.Model):
    _name = "old.time"
    _description = "Old Time In Out"

    date = fields.Date('Date', store=True)
    name = fields.Char('Name', store=True)
    cs = fields.Char('CS Number', store=True)
    timein = fields.Char('TimeIn', store=True)
    timeout = fields.Char('TimeOut', store=True)
    status1 = fields.Char('Status1', store=True)
    status2 = fields.Char('Status2', store=True)
    bas = fields.Char('BAS', store=True)
    branch = fields.Char('Branch', store=True)


class BasicPackage(models.Model):
    _name = "basic.package"
    _description = "Basic Package"

    bank = fields.Many2one('res.partner', 'Bank', store=True)
    name = fields.Char('Name', store=True)
    product_lines = fields.One2many('basic.package.items', 'product_basic_package_line', 'Items', store=True)


class BasicPackageItems(models.Model):
    _name = "basic.package.items"
    _description = "Basic Package Items"

    product_basic_package_line = fields.Many2one('basic.package', 'Product Line', store=True)
    courier_sheet_product_line = fields.Many2one('courier.sheet', 'Product Line', store=True)
    products = fields.Many2one('product.template', 'Products', store=True)
    courier_sheet_products = fields.Many2one('product.items', 'Products', store=True)
    faulty_sheet_products = fields.Many2one('faulty.devices', 'Products', store=True)
    stock_return_products = fields.Many2one('stock.return', 'Products', store=True)
    quantity = fields.Float('Quantity', store=True)
    stock_sheet_date = fields.Date(related='stock_return_products.date', string='Date', readonly=True)
    product_type = fields.Selection([('New', 'New'), ('Used', 'Used'), ('Faulty', 'Faulty')], 'Type', default='New',
                                    store=True)
    type = fields.Selection([('For Technician', 'For Technician'), ('For Customer', 'For Customer'),
                             ('Handover To Warehouse', 'Handover To Warehouse')], 'Type', store=True)
    customer = fields.Many2one('res.partner', 'Customer/Technician', store=True, required=True)
    ref_to = fields.Char('Reference', store=True)
    location = fields.Char('Location', store=True)
    cs_number = fields.Char('CS Number', store=True)
    branch_code = fields.Char('Branch Code', store=True)
    status = fields.Selection([('Available', 'Available'), ('Unavailable', 'Unavailable')], 'Status', store=True,
                              default='Available')
    req_ref = fields.Char('Req. #')

    @api.onchange('customer')
    def cal_cs_bc(self):
        if self.customer.customer_rank:
            self.location = self.customer.city
            self.cs_number = self.customer.cs_number
            self.branch_code = self.customer.branch_code
        else:
            self.location = self.customer.city


class CourierSheet(models.Model):
    _name = "courier.sheet"
    _description = "Courier Sheet"
    _rec_name = "partner_id"

    technician_name = fields.Many2one('hr.employee', 'Technician Name', domain="[('department_id','=','Technician')]")
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    cs_number = fields.Char(related='partner_id.cs_number', string='CS Number', readonly=True)
    city = fields.Char(related='partner_id.city', string='City', readonly=True)
    branch_code = fields.Char(related='partner_id.branch_code', string='Branch Code', readonly=True)
    bank_code = fields.Char(related='partner_id.bank_code', string='Bank Code', readonly=True)
    monitoring_address = fields.Char(related='partner_id.street', string='Bank address', readonly=True)
    date = fields.Date('Date', store=True, required=True, default=lambda self: datetime.now().strftime('%Y-%m-%d'))
    complaint_reference = fields.Integer('Complaint/Task Reference', store=True)
    tcs_receipt = fields.Char('TCS Receipt No.', store=True, size=30)
    remarks = fields.Text('TCS Delivery Status', store=True)
    devices = fields.Char('Devices', store=True, compute='_compute_devices_details')
    qty = fields.Char('Qty', store=True, compute='_compute_devices_details')
    product_lines = fields.One2many('basic.package.items', 'courier_sheet_product_line', 'Items', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State', store=True, default='draft')
    ref = fields.Char('Ref', store=True, compute='_compute_devices_details')
    location = fields.Char(related='technician_name.work_location', string='Technician Work Address', readonly=True)

    @api.depends('product_lines.courier_sheet_products', 'product_lines.quantity')
    def _compute_devices_details(self):
        for record in self:
            devices = []
            qtys = []
            refs = []
            for line in record.product_lines:
                devices.append(line.courier_sheet_products.name)
                qtys.append(str(line.quantity))
                refs.append(line.ref_to)
            record.devices = ', '.join(devices)
            record.qty = ', '.join(qtys)
            record.ref = ', '.join(refs)

    def validate(self):
        self.write({'state': 'confirmed'})

    def cancel(self):
        self.write({'state': 'draft'})

    @api.onchange('complaint_reference')
    def auto_select(self):
        if self.complaint_reference:
            self.env.cr.execute(
                'SELECT id FROM res_partner WHERE id IN (SELECT partner_id FROM project_issue WHERE id = %s)',
                (self.complaint_reference,))
            customer = self.env.cr.dictfetchone()
            if customer:
                self.partner_id = customer['id']


class ProductItems(models.Model):
    _name = "product.items"
    _description = "Product Items"

    name = fields.Char('Name', store=True, size=30)
    product_lines = fields.One2many('product.items.line', 'name', 'Items', store=True)


class ProductItemsLine(models.Model):
    _name = "product.items.line"
    _description = "Product Items Line"

    name = fields.Many2one('product.items', 'Product', store=True)
    products = fields.Many2one('product.template', 'Products', store=True)
    quantity = fields.Float('Quantity', store=True)


class FaultyDevices(models.Model):
    _name = "faulty.devices"
    _description = "Faulty Devices"
    _rec_name = "partner_id"

    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    cs_number = fields.Char(related='partner_id.cs_number', string='CS Number', readonly=True)
    city = fields.Char(related='partner_id.city', string='City', readonly=True)
    branch_code = fields.Char(related='partner_id.branch_code', string='Branch Code', readonly=True)
    bank_code = fields.Char(related='partner_id.bank_code', string='Bank Code', readonly=True)
    monitoring_address = fields.Char(related='partner_id.street', string='Bank address', readonly=True)
    date = fields.Date('Date', store=True, required=True, default=lambda self: datetime.now().strftime('%Y-%m-%d'))
    status = fields.Char('Status', store=True)
    devices_received = fields.Char('New Devices Received', store=True)
    devices_received_qty = fields.Char('New Devices Quantity', store=True)
    product_lines = fields.One2many('basic.package.items', 'faulty_sheet_products', 'Items', store=True)
    devices = fields.Char('Faulty Devices Received', store=True, compute='_compute_devices_details')
    qty = fields.Char('Qty', store=True, compute='_compute_devices_details')

    @api.depends('product_lines.products', 'product_lines.quantity')
    def _compute_devices_details(self):
        for record in self:
            devices = []
            qtys = []
            for line in record.product_lines:
                devices.append(line.products.name)
                qtys.append(str(line.quantity))
            record.devices = ', '.join(devices)
            record.qty = ', '.join(qtys)

class StockReturn(models.Model):
    _name = 'stock.return'
    _description = "Stock Return"

    title = fields.Char('Title', required=True, store=True)
    date = fields.Date('Date', default=lambda self: fields.Date.today(), required=True, store=True)
    req_slip_ref = fields.Char('Requisition Slip Reference', store=True,
                               required=False)
    products = fields.One2many('basic.package.items', 'stock_return_products', 'Items', store=True)
    devices = fields.Char('Devices')
    qty = fields.Char('Qty', store=True)
    ref_cs = fields.Char('Sales Order Reference', store=True)
    ref = fields.Char('Ref', readonly=True, size=15, default=' ')
    ref_two = fields.Char('Ref', readonly=True, default=' ')

    def cumm_product_new_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'New':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod
    

    def cumm_product_used_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'Used':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod

    def cumm_product_faulty_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'Faulty':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod

    # @api.depends('products')
    # def _compute_devices_details(self):
    #     for record in self:
    #         all_customers = ''
    #         req_slip_refs = ''
    #         for line in record.products:
    #             if line.product_type == 'New':
    #                 all_customers += line.customer.name + ","
    #                 req_slip_refs += line.req_ref + ","
    #             elif line.product_type == 'Used':
    #                 all_customers += line.customer.name + ","
    #                 req_slip_refs += line.req_ref + ","
    #             elif line.product_type == 'Faulty':
    #                 all_customers += line.customer.name + ","
    #                 req_slip_refs += line.req_ref + ","
    #         record.devices = all_customers[:-1] if all_customers else ''
    #         record.qty = ','.join(str(line.quantity) for line in record.products)
    #         record.req_slip_ref = req_slip_refs[:-1] if req_slip_refs else ''
    #         emp_ref_two = self.env['mutual.requisition'].search([('ref_two', '=', None)])
    #         if emp_ref_two:
    #             record._append_ref_two(emp_ref_two)
    #
    # def _append_ref_two(self, lst):
    #     for item in lst:
    #         itemlst = self.env['basic.package.items'].search([('req_slip', '=', item.id)])
    #         cumm_prods = ','.join(str(line.cs_number) for line in itemlst)
    #         # Update logic for mutual_requisition
    #         # item.write({'ref_two': cumm_prods})


class MarkAttendance(models.Model):
    _name = 'mark.attendance'
    _description = "Mark Attendance"

    employee_id = fields.Many2one('hr.employee', 'Name', store=True, readonly=True)
    check_in = fields.Datetime('Check In', store=True)
    check_in_view = fields.Datetime('Time In', store=True)
    status = fields.Selection([('Present', 'Present'), ('Absent', 'Absent')], string='Status', store=True)


class SmsReport(models.Model):
    _name = 'sms.report'
    _description = "SMS Report"

    date = fields.Datetime('Date', default=lambda self: fields.Datetime.now(), store=True)
    sms = fields.Text('SMS', store=True)
    to = fields.Char('To', store=True)
    status = fields.Char('Status', store=True)
    type = fields.Char('Type', store=True)


class AttendanceLogs(models.Model):
    _name = 'attendance.logs'
    _description = "Attendance Logs"

    text = fields.Char('Text', store=True)
    contact = fields.Char('Contact', store=True)
    date_ = fields.Char('Date', store=True)
    time_ = fields.Char('Time', store=True)

    @api.model
    def cron_tech_attendance(self):
        mark_attendance = self.env['mark.attendance']
        employees = self.env['hr.employee'].search([('department_id', '=', 1)], order='id asc')
        for employee in employees:
            present_employee = self.env['attendance.logs'].search(
                [('contact', '=', employee.work_phone), ('date_', '=', fields.Date.today())], limit=1)
            if present_employee:
                vals = {
                    'employee_id': employee.id,
                    'check_in': present_employee.date_ + " " + present_employee.time_,
                    'check_in_view': datetime.strptime(present_employee.date_ + " " + present_employee.time_,
                                                       "%Y-%m-%d %H:%M:%S") - timedelta(hours=5),
                    'status': 'Present'
                }
                mark_attendance.create(vals)
            else:
                vals = {
                    'employee_id': employee.id,
                    'status': 'Absent'
                }
                mark_attendance.create(vals)
        print("Job done.......................")
