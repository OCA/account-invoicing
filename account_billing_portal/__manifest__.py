# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Billing Portal",
    "version": "18.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account_billing"],
    "data": [
        "security/account_billing_portal_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/account_billing_portal_templates.xml",
        "views/account_billing_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "development_status": "Alpha",
    "installable": True,
}
