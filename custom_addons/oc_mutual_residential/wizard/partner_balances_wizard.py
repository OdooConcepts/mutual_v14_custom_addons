from odoo import _, fields, models


class PartnerBalanceReportWizard(models.TransientModel):
    _name = "partner.balance.report.wizard"
    _description = "Partner Balance Report Wizard"

    company_id = fields.Many2one('res.company', string='Company')
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date TO", required=True)

    def get_balance(self):
        # mutual security system account id
        if self.env.company.id == 3:
            id = 429
        #     mutual security account id
        if self.env.company.id == 2:
            id = 174
            # mutual security system pvt.ltd account id
        if self.env.company.id == 5:
            id = 1722
        self.env.cr.execute("""select cs_category,sum(account_move_line.debit)as debit,sum(account_move_line.credit) as credit,
         sum(account_move_line.debit) - sum(account_move_line.credit) as balance from res_partner 
        inner join account_move_line on res_partner.id = account_move_line.partner_id 
        inner join account_move on account_move_line.move_id = account_move.id
        where account_move_line.account_id='%s' and account_move.state = 'posted'
         and account_move_line.date between '%s' and '%s' group by cs_category
         order by cs_category""" % (id, self.date_from, self.date_to))
        return self.env.cr.dictfetchall()

    def get_initialbalance(self):
        self.env.cr.execute("""select sum(account_move_line.debit) - sum(account_move_line.credit) as initialbalance from 
        account_move_line where account_id=429 and parent_state='posted' and date < '%s' """ % (self.date_from));
        return self.env.cr.dictfetchall()

    def action_print_report(self):
        self.company_id = self.env.company.id
        data = {
            'forms_data': self.read()[0],
            'form': self.get_initialbalance(),
            'balance': self.get_balance(),
        }
        return self.env.ref('oc_mutual_residential.action_report_partner_balances').report_action(self, data=data)
