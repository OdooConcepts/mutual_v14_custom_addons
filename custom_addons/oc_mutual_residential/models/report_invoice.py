from odoo import api, models


class InvoiceReport(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env['account.move']
        docs = self.env['account.move'].browse(docids)
        invoices = model.search_read(
            [('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial']),
             ('partner_id', '=', docs.partner_id.id), ('id', '!=', docs.id)])
        balance_total = 0
        total = 0
        for invoice in invoices:
            balance_sum = float(invoice['amount_residual'])
            balance_total += balance_sum
            total = balance_total + docs.amount_residual
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': invoices,
            'docs': docs,
            'balance': balance_total,
            'total': total,
            'monitoring_from': docs.monitoring_period_from,
            'monitoring_to': docs.monitoring_period_to
        }


class MonitoringInvoiceReport(models.AbstractModel):
    _name = 'report.oc_mutual_residential.report_invoice_monitoring'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env['account.move']
        docs = self.env['account.move'].browse(docids)
        invoices = model.search_read(
            [('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial']),
             ('partner_id', '=', docs.partner_id.id), ('id', '!=', docs.id)])
        customer_invoices = model.search_read(
            [('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial','paid']),
             ('partner_id', '=', docs.partner_id.id), ('id', '!=', docs.id)],order='invoice_date desc', limit=5)
        balance_total = 0
        total = 0

        for invoice in invoices:
            balance_sum = float(invoice['amount_residual'])
            balance_total += balance_sum
            total = balance_total + docs.amount_residual
        grand_total_amount_in_words = self._get_amount_in_words(total)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': invoices,
            'customer_data': customer_invoices,
            'docs': docs,
            'balance': balance_total,
            'total': total,
            'monitoring_from': docs.monitoring_period_from,
            'monitoring_to': docs.monitoring_period_to,
            'grand_total_amount_in_words': grand_total_amount_in_words,
        }


    def _get_amount_in_words(self,total):
        return str(self.env['res.currency'].search([('name','=','PKR')], limit=1).amount_to_text(round(total))) +' only'


# class Monitoring2InvoiceReport(models.AbstractModel):
#     _name = 'report.oc_mutual_residential.custom_mspl_invoice'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
    #     query = self.env.cr.execute("""select sum(debit-credit) as total
    #      from account_move_line where partner_id=%s"""%(docs.partner_id.id))
    #     model = self.env['account.move']
    #     docs = self.env['account.move'].browse(docids)
    #     invoices = model.search_read(
    #         [('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial']),
    #          ('partner_id', '=', docs.partner_id.id), ('id', '!=', docs.id)])
    #     balance_total = 0
    #     total = 0
    #     for invoice in invoices:
    #         balance_sum = float(invoice['amount_residual'])
    #         balance_total += balance_sum
    #         total = balance_total + docs.amount_residual
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': model,
    #         'data': invoices,
    #         'docs': docs,
    #         'balance': balance_total,
    #         'total': total,
    #         'monitoring_from': docs.monitoring_period_from,
    #         'monitoring_to': docs.monitoring_period_to
    #     }
