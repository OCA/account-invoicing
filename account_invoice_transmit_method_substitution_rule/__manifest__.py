# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Transmit Method Substitution Rule",
    "summary": """
        This addon allow to set substitution rules for transmit method""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account_invoice_transmit_method"],
    "data": [
        "security/transmit_method_substitution_rule.xml",
        "views/transmit_method_substitution_rule.xml",
    ],
    "demo": ["demo/transmit_method_substitution_rule.xml"],
}
