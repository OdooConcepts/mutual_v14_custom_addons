from odoo import fields, models

class AttendanceMigration(models.Model):
    _name = "attendance.migration"

    employee_id = fields.Integer(string='Employee ID')
    checkin = fields.Datetime(string='Check In')
    checkout = fields.Datetime(string='Check Out')
    old_system_id = fields.Integer(string='Old System ID')

class SalesOrderMigration(models.Model):
    _name = "sales.order.migration"

    order_id = fields.Integer(string='Old System ID')
    partner_id = fields.Integer(string='Customer ID')
    order_reference = fields.Char("Order Reference")
    delivery_address_id = fields.Integer(string='Delivery Address ID')
    shipping_address_id = fields.Integer(string='Shipping Address ID')
    sales_team_id = fields.Integer(string='Sales Team ID')
    warehouse_id = fields.Integer("Warehouse ID")
    sales_person_id = fields.Integer(string='Sales Person ID')
    validity = fields.Date("Validity")
    price_list_id = fields.Integer(string='Price List ID')
    terms_and_conditions = fields.Text(string='Terms and Conditions')

class SalesOrderLineMigration(models.Model):
    _name = "sales.order.line.migration"

    order_id = fields.Integer(string='Order ID')
    description = fields.Text(string='Description')
    qty = fields.Float("Quantity")
    unit_price = fields.Float(string='Unit Price')
    uom = fields.Char(string='UoM')
    cost = fields.Float(string='Cost')
    product_id = fields.Integer("Product ID")
    order_lines_sequence = fields.Integer(string='Order Lines Sequence')
    order_line_id = fields.Integer("Order Line ID")
    opportunity_id = fields.Integer("Opportunity ID")

class ComplaintMigration(models.Model):
    _name = "complaint.migration"

    x_id = fields.Integer(string='Old System ID')
    x_partner_id = fields.Integer(string='Old Partner ID')
    x_description = fields.Char("Description")
    x_stage_id = fields.Integer("Stage ID")
    x_user_id_issue = fields.Integer("User ID Isssue")
    x_contactperson = fields.Char("Contact Person")
    x_responsibleperson = fields.Char("Responsible Person")
    x_additional = fields.Boolean("Additional")
    x_payment = fields.Boolean("Payment Pending")
    x_payment_r = fields.Boolean("Payment Received")
    x_create_uid = fields.Integer("Created bY")
    x_create_date = fields.Datetime("Created Date")
    x_name = fields.Char("Name")
    x_status = fields.Char("Status", default='Done')


class DataMigration(models.Model):
    _name = "data.migration"
    _description = "Oc Data Migration"
    id = fields.Integer(string='Id', required=True, tracking=True)
    company_id = fields.Integer(string='Company Id', tracking=True)
    partner_id = fields.Char(string='Partner Id', tracking=True)
    reconcile_id = fields.Char(string='Reconcile Partial Id', tracking=True)
    credit = fields.Float(string='Credit', tracking=True)
    journal_id = fields.Integer(string='Journal Id', tracking=True)
    state = fields.Char(string='State', tracking=True)
    debit = fields.Float(string='Debit', tracking=True)
    ref = fields.Char(string='Reference', tracking=True)
    account_id = fields.Integer(string='Account Id', tracking=True)
    period_id = fields.Integer(string='Period Id', tracking=True)
    date = fields.Date(string='Date', tracking=True)
    move_id = fields.Integer(string='Move Id', tracking=True)
    name = fields.Char(string='name', tracking=True)
    tax_amount = fields.Char(string='Tax Amount', tracking=True)
    product_id = fields.Integer(string='Product Id', tracking=True)
    account_tax_id = fields.Integer(string='Account Tax Id', tracking=True)
    product_uom_id = fields.Integer(string='Product UOM Id', tracking=True)
    amount_currency = fields.Integer(string='Amount Currency', tracking=True)
    quantity = fields.Integer(string='Quantity')



class invoiceMigration(models.Model):
    _name = 'invoice.migration'

    old_partner_id = fields.Integer(string='Old Partner ID')
    invoice_date = fields.Date(string='Invoice Date')
    old_system_id = fields.Integer(string='Old System ID')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    courier = fields.Boolean(string='Courier')
    payment_received = fields.Boolean(string='Payment Received')
    po_dd = fields.Char(string='PO/DD')
    cheque_no = fields.Char(string='Cheque No.')
    cheque_date = fields.Char(string='Cheque Date')
    cheque_received_date = fields.Char(string='Cheque Received Date')
    actual_received_amount = fields.Char(string='Actual Received Amount')


class invoiceLinesMigration(models.Model):
    _name = 'invoice.lines.migration'

    old_product_id = fields.Integer(string='Old Product ID')
    old_sytem_id = fields.Integer(string='Old System ID')
    old_account_id = fields.Integer(string='Account ID')
    section = fields.Char(string='Section')
    effect_on_inventory = fields.Char(string='Effect On Inventory')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    tax = fields.Char(string='Tax')
