# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

{
    "name": "Account Invoice Supplier Self Invoice Tax Note",
    "version": "11.0.1.0.0",
    "author": "Creu Blanca, "
              "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_supplier_self_invoice",
        "account_invoice_tax_note",
    ],
    "data": [
        "views/report_self_invoice.xml"
    ],
    "auto_install": True,
    "installable": True,
}
