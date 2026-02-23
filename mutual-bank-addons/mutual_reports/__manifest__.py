{
    'name': 'Mutual Reporting',
    'summary': 'Custom Module for all Reports',
    'description': """
        This module provides custom reports for mutual accounting and projects.
    """,
    'author': "Team Emotive Labs",
    'category': 'Mutual',
    'version': '0.1',
    'website': "https://www.emotivelabs.ca",

    # Any module necessary for this one to work correctly
    'depends': [
        'sale',
        'account',
        'mutual_sales',
        'mutual_project',
        'mutual_invoice'
    ],

    # Data files which are necessary for this module to work
    'data': [
        'mutual_reports_reports.xml',
        'views/mutual_header_footer.xml',
        'views/tax_break_up_invoice.xml',
        'views/wiz_recovery_report.xml',
        #'views/custom_sales_tax_invoice_pdf.xml',
        'views/custom_report_mutual_stock_return_pdf.xml',
        'views/custom_courier_sheet_report.xml',
        'views/custom_report_mutual_req_pdf.xml',
        'views/custom_layouts.xml',
        'views/report_acknowledgment_receipt.xml',
        'views/report_issue_pdf.xml',
        'views/report_task_pdf.xml',
        'views/report_history_pdf.xml',
        'views/summary_sheet_pdf.xml',
        'views/technician_info_pdf.xml',
        #'views/customer_biodata_pdf.xml',
        'views/custom_additional_invoice_pdf.xml',
        'views/custom_monitoring_invoice_pdf.xml',
        'wizard/wiz_recovery_report_view.xml',
        'wizard/wizard_invoices_writeoff_view.xml',
        'views/account_invoice.xml',
        'wiz_report_menuitem.xml',
        # Uncomment the line below if 'wizard/wiz_report_selection.xml' is needed
        # 'wizard/wiz_report_selection.xml',
    ],

    # 'qweb': [
    #     'static/src/xml/module_name.xml',
    # ],

    # Only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
