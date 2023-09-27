# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice line with sequence number",
    "version": "15.0.1.0.0",
    "summary": "Adds sequence field on invoice lines to manage its order.",
    "category": "Accounting",
    "author": "Camptocamp, "
    "ForgeFlow, "
    "Serpent CS, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "data": ["views/account_invoice_view.xml", "views/report_invoice.xml"],
    "depends": ["account"],
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "installable": True,
}
