# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice - Quantity Multiplier Update",
    "summary": "In the invoice Supplierinfo wizard,"
    " allow to change the Quantity Multiplier field",
    "version": "12.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "GRAP,Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "license": "AGPL-3",
    "depends": [
        "account_invoice_supplierinfo_update",
        "product_supplierinfo_qty_multiplier",
    ],
    "installable": True,
    "auto_install": True,
    "data": [
        "wizard/wizard_update_invoice_supplierinfo.xml",
    ],
}
