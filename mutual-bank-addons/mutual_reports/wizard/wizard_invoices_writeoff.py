from odoo import models, fields, api
from odoo.exceptions import UserError

class WizardReports(models.TransientModel):
    _name = 'wiz.invoices.writeoff'
    _description = 'PDF Reports for showing all disconnection, reconnection'

    date = fields.Date('Invoice Date', required=True)
    cheque_no = fields.Char('Cheque No', required=True)
    bank_code = fields.Selection(
        [('FBL', 'FBL'), ('JSBL', 'JSBL')], required=True, string='Bank Code'
    )
    invoice_amount = fields.Float('Invoice Amount', required=True)
    received_amount = fields.Float('Received Amount', required=True)

    def inv_status_changed(self, central, south, north, main):
        query = """
            UPDATE account_move
            SET state='cancel', payment_received=True, courier=True,
                cheque_no=%s,
                comment='Payment has been received against parent invoice therefore user cancelled this invoice'
            FROM res_partner
            WHERE account_move.partner_id = res_partner.id
              AND account_move.state='draft'
              AND res_partner.bank_code=%s
              AND account_move.invoice_date=%s
              AND account_move.amount_total=%s
              AND account_move.partner_id NOT IN (%s, %s, %s, %s)
        """
        params = (
            self.cheque_no,
            self.bank_code,
            self.date,
            self.invoice_amount,
            central,
            south,
            north,
            main
        )
        self.env.cr.execute(query, params)
        return True

    def inv_status_change_request(self):
        if self.bank_code == 'FBL':
            fbl_central = 9464
            fbl_south = 9522
            fbl_north = 9450
            fbl_main = 9572
            result = self.inv_status_changed(fbl_central, fbl_south, fbl_north, fbl_main)
            return result

        if self.bank_code == 'JSBL':
            jsbl_central = 11056
            jsbl_south = 11057
            jsbl_north = 11058
            jsbl_main = 3349
            result = self.inv_status_changed(jsbl_central, jsbl_south, jsbl_north, jsbl_main)
            return result

        raise UserError("Records have been successfully updated")
