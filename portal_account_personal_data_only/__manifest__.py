# Copyright 2018-19 Tecnativa S.L. - David Vidal
# Copyright 2022 Moduon Team SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Portal Accounting Personal Data Only",
    "version": "15.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Moduon, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["security/security.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
