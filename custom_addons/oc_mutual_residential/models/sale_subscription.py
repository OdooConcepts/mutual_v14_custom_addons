from odoo import api, fields, models,_
from datetime import date, timedelta,datetime
import logging
import traceback
import calendar
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class SalesSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    old_system_id = fields.Integer()

class SalesSubscription(models.Model):
    _inherit = 'sale.subscription'

    old_system_id = fields.Integer()
    from_date = fields.Date()
    to_date = fields.Date()
    cs_number = fields.Char('CS Number', related='partner_id.cs_number')
    subscription_type = fields.Selection([('monitoring_service','Monitoring Service'),('sms_service','SMS Service')])

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if not self.recurring_next_date:
            res.update({
                "invoice_date": self.recurring_next_date,
                "monitoring_period_from": False,
                "monitoring_period_to": False
            })
            return res

        date_format = "%Y-%m-%d"
        from_date = datetime.strptime(str(self.recurring_next_date), date_format)
        number_of_days = calendar.monthrange(from_date.year, from_date.month)[1]

        valid_services = ["Service MS", "Service MSS", "Service MSPL","SMS Subscription Charges MSS","SMS Subscription Charges MS","SMS Subscription Charges MSPL"]

        for line in res['invoice_line_ids']:
            product = self.env['product.product'].sudo().browse(line[2]['product_id'])
            service_name = product.name
            if service_name not in valid_services:
                continue

            if number_of_days in [28, 29, 30, 31]:
                if from_date.day == 1:
                    offset = 20
                elif from_date.day in [11, 21]:
                    offset = 18 if number_of_days == 28 else 19 if number_of_days == 29 else 20 if number_of_days == 30 else 21
                else:
                    continue

                from_ = from_date + timedelta(days=offset)
                to = from_ + relativedelta(months=int(line[2]['quantity'])) - timedelta(days=1)
                self.from_date = from_.strftime("%Y-%m-%d")
                self.to_date = to.strftime("%Y-%m-%d")

                if self.company_id == 3:
                    self.date = self.from_date

                line[2]['name'] = line[2]['name']+" "+ f"from {self.from_date} to {self.to_date}"
                res.update({
                    "invoice_date": self.recurring_next_date,
                    "monitoring_period_from": self.from_date,
                    "monitoring_period_to": self.to_date
                })
            else:
                res.update({
                    "invoice_date": self.recurring_next_date,
                    "monitoring_period_from": False,
                    "monitoring_period_to": False
                })

        return res












