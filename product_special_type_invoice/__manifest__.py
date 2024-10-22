# Copyright 2012-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Special Type on Invoice",
    "version": "16.0.1.0.1",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Beta",
    "category": "Invoicing",
    "summary": """
According to the products special types (discount, advance, delivery),
compute totals on invoices.
""",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "product_special_type",
        "account",
    ],
    "data": [
        "views/account_invoice.xml",
        "reports/report_invoice.xml",
    ],
    "installable": True,
}
