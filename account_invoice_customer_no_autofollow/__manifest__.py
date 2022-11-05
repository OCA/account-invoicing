# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Customer No Autofollow",
    "summary": "Do not add customer as follower in Invoices",
    "author": "Cetmix,Odoo Community Association (OCA)",
    "version": "13.0.1.0.0",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account",
    "depends": ["account"],
    "maintainers": ["dessanhemrayev", "CetmixGitDrone"],
    "data": ["views/res_config_settings.xml"],
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "installable": True,
    "auto_install": False,
    "application": False,
}
