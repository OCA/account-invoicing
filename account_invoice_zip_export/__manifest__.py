##############################################################################
#    License AGPL-3.0
##############################################################################
{
    "name": "Export Invoices",
    "summary": """Export multiple invoices PDF in Zip
    Allows User To Select From Date and To Date For Export Invoices in ZIP Format
    For Selected Invoice status.
    For this Go To The Invoice > Click On Reporting Menu > Select the Export Invoices.
    """,
    "version": "15.0.1.0.0",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/invoice_pdf_export_view.xml",
    ],
    "author": "Nitrokey GmbH," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-invoicing",
}
