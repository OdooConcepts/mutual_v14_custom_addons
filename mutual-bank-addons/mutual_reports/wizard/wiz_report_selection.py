from odoo import models, fields, api
import xlwt
from xlwt import *
import io
import xlsxwriter
import base64


class ReportSelection(models.TransientModel):
    _name = 'wiz.report.selection'
    _description = 'For Excel Report Selection'

    select = fields.Selection(
        [
            ('additional', 'Additional Invoice Report'),
            ('monitoring', 'Monitoring Report'),
            ('tax_break', 'Tax Break-Up Invoice')
        ], required=True)
    report = fields.Binary('Report Data', readonly=True)
    report_name = fields.Char('File Name', store=True, readonly=True)

    def select_report_type(self):
        if self.select == 'additional':
            return self.additional_excel_report()
        elif self.select == 'monitoring':
            return self.monitoring_invoice()
        elif self.select == 'tax_break':
            return self.tax_break_inv()
        else:
            raise ValueError('No Report Type Selected')

    def additional_excel_report(self):
        active_id = self.env.context.get('active_id', False)
        record = self.env['account.move'].browse(active_id)

        # Header formatting
        borders_header = Borders()
        borders_header.left = 3
        borders_header.right = 3
        borders_header.top = 3
        borders_header.bottom = 3

        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER

        # Total amount formatting
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Additional')
        ws.protect = True
        fp = io.BytesIO()

        row = 10
        col = 0

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200;")

        ws.write_merge(0, 0, 0, 10, 'Additional Invoice', header_style)
        ws.write(2, 1, record.partner_id.name, sub_header_style)
        ws.write(5, 5, 'STN', sub_header_style)
        ws.write(5, 6, '17-00-3764-757-19', sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2, record.partner_id.vat, value_style)
        ws.write(7, 1, 'INVOICE REF #', sub_header_style)
        ws.write(7, 4, record.id, value_style)

        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Quantity', sub_header_style)
        ws.write(9, 8, 'Unit Price', sub_header_style)
        ws.write(9, 10, 'Amount', sub_header_style)

        for line in record.invoice_line_ids:
            ws.write(row, 0, line.name, value_style)
            ws.write(row, 6, line.quantity, value_style)
            ws.write(row, 8, line.price_unit, value_style)
            ws.write(row, 10, line.price_subtotal, value_style)
            row += 1

        ws.write(24, 8, 'Total', sub_header_style)
        ws.write(24, 10, round(record.amount_total), total_format)

        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        self.write({'report': out, 'report_name': 'additional.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
        }

    def monitoring_invoice(self):
        active_id = self.env.context.get('active_id', False)
        record = self.env['account.move'].browse(active_id)

        # Header formatting
        borders_header = Borders()
        borders_header.left = 1
        borders_header.right = 1
        borders_header.top = 1
        borders_header.bottom = 1

        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER

        # Total amount formatting
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Monitoring')
        ws.protect = True
        fp = io.BytesIO()

        row = 10
        col = 0

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200;")

        ws.write_merge(0, 0, 0, 8, 'Monitoring Invoice', header_style)
        ws.write(2, 1, record.partner_id.name, sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2, record.partner_id.vat, value_style)
        ws.write(7, 1, 'INVOICE REF #', sub_header_style)
        ws.write(7, 3, record.id, value_style)

        # One to many field data
        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Billing Period', sub_header_style)
        ws.write(9, 8, 'Amount', sub_header_style)

        for line in record.invoice_line_ids:
            if line.product_id.name == 'Monitoring charges' and record.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row += 1
            elif line.product_id.name == 'Monitoring charges' and record.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row += 1

        for line in record.invoice_line_ids:
            if line.product_id.name == 'Monitoring charges':
                ws.write(row, 6, record.invoice_date_due, value_style)
                ws.write(row, 7, record.invoice_date_due, value_style)
                row += 1

        ws.write(24, 6, 'Total', sub_header_style)
        ws.write(24, 8, round(record.amount_total), total_format)

        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        self.write({'report': out, 'report_name': 'monitoring_invoice.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
        }

    def tax_break_inv(self):
        active_id = self.env.context.get('active_id', False)
        record = self.env['account.move'].browse(active_id)

        # Header formatting
        borders_header = Borders()
        borders_header.left = 1
        borders_header.right = 1
        borders_header.top = 1
        borders_header.bottom = 1

        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        # Total amount formatting
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Tax Break-Up')
        ws.protect = True
        fp = io.BytesIO()

        row = 10
        col = 0

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200;")

        ws.write_merge(0, 0, 0, 8, 'Tax Break-Up Invoice', header_style)
        ws.write(2, 1, record.partner_id.name, sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2, record.partner_id.vat, value_style)
        ws.write(7, 1, 'INVOICE REF #', sub_header_style)
        ws.write(7, 3, record.id, value_style)

        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Billing Period', sub_header_style)
        ws.write(9, 8, 'Amount', sub_header_style)

        for line in record.invoice_line_ids:
            if line.product_id.name == 'Monitoring charges' and record.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row += 1
            elif line.product_id.name == 'Monitoring charges' and record.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row += 1

        for line in record.invoice_line_ids:
            if line.product_id.name == 'Monitoring charges':
                ws.write(row, 6, record.invoice_date_due, value_style)
                ws.write(row, 7, record.invoice_date_due, value_style)
                row += 1

        ws.write(24, 6, 'Total', sub_header_style)
        ws.write(24, 8, round(record.amount_total), total_format)

        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        self.write({'report': out, 'report_name': 'tax_break_invoice.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
        }
