# Copyright 2017 Creu Blanca
# Copyright 2022 Moduon
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

{
    "name": "Purchase Self Invoice",
    "version": "15.0.1.3.0",
    "author": "CreuBlanca, Moduon, Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "data/mail_template_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/report_self_invoice.xml",
    ],
    "installable": True,
}
