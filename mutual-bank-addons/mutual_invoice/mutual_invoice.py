from odoo import models, fields, api
import re
from datetime import datetime


class InvoiceLine(models.Model):
    _inherit = 'account.move.line'

    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    effect_on_inventory = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Effect On Inventory', default='Yes')
    tax_amount = fields.Float(string='Tax Amount')
    ntn = fields.Char(related='partner_id.vat', string='NTN', store=True)

    # @api.depends('price_unit', 'quantity', 'tax_ids')
    # def compute_tax_amount(self):
    #     for line in self:
    #         tax_amount = sum((line.quantity * line.price_unit * tax.amount) / 100 for tax in line.tax_ids)
    #         line.tax_amount = round(tax_amount, 2)


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    first_call = fields.Date(string='First Call')
    next_call = fields.Date(string='Next Call')
    #product_line = fields.Char(string='Products', compute='compute_product_line')
    product_line = fields.Char(string='Products')
    product_check = fields.Boolean(string='Show Product')
    show_tax = fields.Boolean(string='Show Tax')
    ntn = fields.Char(string='NTN', default="3764757-1", readonly=True)
    sales_tax_no = fields.Char(string='STN', default="17-00-3764-757-19", readonly=True)
    courier = fields.Boolean(string='Couriered', store=True)
    payment_received = fields.Boolean(string='Payment Received', store=True, tracking=True)
    bank_name = fields.Char(string='Name', related='partner_id.name', readonly=True)
    bank_cs_invoice = fields.Char(string='CS Number', related='partner_id.cs_number', readonly=True)
    bank_code_invoice = fields.Char(string='Bank code', related='partner_id.bank_code', readonly=True)
    branch_code_invoice = fields.Char(string='Branch code', related='partner_id.branch_code', readonly=True)
    remarks = fields.Text(string='Follow Up')
    po_dd = fields.Selection([('PO', 'PO'), ('DD', 'DD')], string='PO/DD')
    cheque_date = fields.Date(string='Cheque Received Date',tracking=True)
    cheque_no = fields.Char(string='Cheque no.',tracking=True)
    cheque_date_customer = fields.Date(string='Cheque Date',tracking=True)
    actual_amount = fields.Float(string='Actual received amount',tracking=True)
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    pay_remarks = fields.Char(string='Payment Remarks')
    invoice_date = fields.Date(string='Invoice Date')
    sales_tax = fields.Float(string='Total Sales Tax 17%', readonly=True)
    srb_tax = fields.Float(string='SRB 19%', readonly=True)
    product_sales_amount = fields.Float(string='Net Product Sales Amount', readonly=True)
    monitoring_sales_amount = fields.Float(string='Net Monitoring Sales Amount', readonly=True)
    maintenance_amount = fields.Float(string='Maintenance Amount', readonly=True)
    installation_amount = fields.Float(string='Installation Amount', readonly=True)
    total_monitoring_amount = fields.Float(string='Total Monitoring', readonly=True)
    total_product_amount = fields.Float(string='Total Product Sales', readonly=True)
    invoice_no_reference = fields.Char(string='Invoice Number Reference')
    purchase_order_no = fields.Char(string='PO no.')
    purchase_order_Date = fields.Date(string='Dated')
    invoice_subject = fields.Char(string='Subject')
    hide_cust_ntn_strn_no = fields.Boolean(string='Hide Customer STRN & NTN no')
    hide_mutual_strn_no = fields.Boolean(string='Hide Mutual STRN no')
    hide_mutual_ntn_no = fields.Boolean(string='Hide Mutual NTN no')
    hide_purchase_order_detail = fields.Boolean(string='Hide Purchase Order Detail')
    tax_10_percent = fields.Float(string='Tax 10 Percent', readonly=True)
    tax_17_percent = fields.Float(string='Tax 17 Percent', readonly=True)
    tax_19_percent = fields.Float(string='Tax 19 Percent', readonly=True)
    tax_19_5_percent = fields.Float(string='Tax 19.5 Percent', readonly=True)

    # @api.depends('state')
    # def compute_auto_marking(self):
    #     for record in self:
    #         if record.state == 'paid':
    #             record.courier = True
    #             record.payment_received = True

    # @api.depends('courier', 'invoice_line_ids')
    # def compute_product_line(self):
    #     for record in self:
    #         if record.courier:
    #             product_names = [line.name for line in record.invoice_line_ids]
    #             record.product_line = ','.join(product_names)

    @api.depends('invoice_line_ids.tax_ids', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.account_id')
    def compute_auto_tax(self):
        for record in self:
            record.sales_tax = 0.0
            record.srb_tax = 0.0
            record.product_sales_amount = 0.0
            record.monitoring_sales_amount = 0.0
            record.maintenance_amount = 0.0
            record.installation_amount = 0.0
            record.total_monitoring_amount = 0.0
            record.total_product_amount = 0.0

            for line in record.invoice_line_ids:
                for tax in line.tax_ids:
                    if tax.description == 'Sales Tax Output 17.00%':
                        record.show_tax = True
                        record.sales_tax += line.price_subtotal * 17 / 100
                        record.product_sales_amount += line.price_subtotal
                        record.total_product_amount += record.sales_tax + record.product_sales_amount
                    elif line.account_id.name == 'Monitoring Sales' and tax.description == 'SRB 19%':
                        record.show_tax = True
                        record.srb_tax += line.price_subtotal * 19 / 100
                        record.monitoring_sales_amount += line.price_subtotal
                        record.total_monitoring_amount += record.srb_tax + record.monitoring_sales_amount
                    elif line.account_id.name == 'Monitoring Sales' and tax.description == 'PRB 19.5%':
                        record.show_tax = True
                        record.srb_tax += line.price_subtotal * 19.5 / 100
                        record.monitoring_sales_amount += line.price_subtotal
                        record.total_monitoring_amount += record.srb_tax + record.monitoring_sales_amount
                    elif line.account_id.name == 'Monitoring Sales' and tax.description == 'KPK 19.5%':
                        record.show_tax = True
                        record.srb_tax += line.price_subtotal * 19.5 / 100
                        record.monitoring_sales_amount += line.price_subtotal
                        record.total_monitoring_amount += record.srb_tax + record.monitoring_sales_amount
                    elif line.account_id.name == 'Maintenance Revenue' and tax.amount != 0.1:
                        record.maintenance_amount += line.price_subtotal
                    elif line.account_id.name == 'Installation Revenue' and tax.amount != 0.1:
                        record.installation_amount += line.price_subtotal
                    elif tax.amount == 0.1:
                        record.tax_10_percent = line.price_subtotal * tax.amount

    # @api.onchange('remarks')
    # def followup_date(self):
    #     if self.remarks and re.findall(str(datetime.now().date()), self.remarks):
    #         self.remarks = f"{self.remarks}\n{datetime.now().date()}"

    def compute_roundoff(self):
        for record in self:
            record.amount_total = round(record.amount_total, 2)

class SummarySheet(models.Model):
    _name = 'summary_sheet'

    customer = fields.Many2one('res.partner', string='Customer', required=True, domain="[('customer_rank','=',True)]")
    name = fields.Char(string='Name')
    summary_sheets = fields.One2many('billing_period', 'dummy', string='Summary Sheets')
    sale_tax = fields.Boolean(string='Sales Tax')
    maintenance_charges = fields.Boolean(string='Maintenance Charges')
    total = fields.Float(string='Total Amount', compute='_compute_total_ss')

    @api.depends('summary_sheets.total_amount_with_sales_tax')
    def _compute_total_ss(self):
        for record in self:
            total = sum(line.total_amount_with_sales_tax for line in record.summary_sheets)
            record.total = round(total, 2)


class BillingPeriod(models.Model):
    _name = 'billing_period'

    dummy = fields.Char(string='dummy')
    cs_number = fields.Char(string='CS Number')
    branch_code = fields.Char(string='Branch Code')
    address1 = fields.Char(string='Address 1')
    address2 = fields.Char(string='Address 2')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    service_period = fields.Integer(string='Service Period')
    sales_tax = fields.Float(string='Sales Tax in %')
    sales_tax_amount = fields.Float(string='Sales Tax in amount', compute='compute_total_in_sales_tax')
    basic_amount = fields.Float(string='Monitoring Amount per month')
    maintenance_basic_amount = fields.Float(string='Maintenance Amount per month')
    total_moni = fields.Float(string='Total Monitoring', compute='compute_total_in_sales_tax')
    total_ment = fields.Float(string='Total Maintenance', compute='compute_total_in_sales_tax')
    total_amount_ex_sales_tax = fields.Float(string='Total billing amount excluding sales tax',
                                             compute='compute_total_in_sales_tax')
    total_amount_with_sales_tax = fields.Float(string='Total billing amount including sales tax',
                                               compute='compute_total_in_sales_tax')

    @api.depends('service_period', 'basic_amount', 'sales_tax', 'maintenance_basic_amount')
    def compute_total_in_sales_tax(self):
        for record in self:
            tax = (record.sales_tax * record.basic_amount) / 100
            record.sales_tax_amount = record.service_period * tax
            record.total_ment = round(record.service_period * record.maintenance_basic_amount, 2)
            record.total_moni = round(record.service_period * record.basic_amount, 2)
            if record.maintenance_basic_amount > 0.0:
                record.total_amount_ex_sales_tax = round((record.service_period * record.basic_amount) + (
                            record.service_period * record.maintenance_basic_amount), 2)
                record.total_amount_with_sales_tax = round(
                    (record.service_period * record.basic_amount) + (record.service_period * tax) + record.total_ment,
                    2)
            else:
                record.total_amount_ex_sales_tax = round(record.service_period * record.basic_amount, 2)
                record.total_amount_with_sales_tax = round(record.total_amount_ex_sales_tax + record.sales_tax_amount,
                                                           2)
