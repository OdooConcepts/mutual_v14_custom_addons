from odoo import models, fields, api

class WizardReports(models.TransientModel):
    _name = 'wiz.reports'
    _description = 'PDF Reports for showing all disconnection, reconnection'

    def pending_invoices(self):
        self.env.cr.execute("""
            SELECT bank_code, SUM(amount_total) AS amount_total, COUNT(amount_total) AS invoices_total
            FROM account_invoice
            INNER JOIN res_partner ON account_invoice.partner_id = res_partner.id
            WHERE account_invoice.courier = True
            AND account_invoice.payment_received = False
            AND account_invoice.state != 'cancel'
            AND account_invoice.state != 'paid'
            AND account_invoice.state != 'open'
            GROUP BY bank_code
        """)
        pendings = self.env.cr.dictfetchall()
        return pendings

    def received_invoices(self):
        self.env.cr.execute("""
            SELECT bank_code, SUM(amount_total) AS amount_total, COUNT(amount_total) AS invoices_total
            FROM account_invoice
            INNER JOIN res_partner ON account_invoice.partner_id = res_partner.id
            WHERE account_invoice.payment_received = True
            AND account_invoice.state != 'cancel'
            GROUP BY bank_code
        """)
        received = self.env.cr.dictfetchall()
        return received

    def print_report(self):
        return self.env.ref('mutual_reports.wiz_recovery_report').report_action(self)
