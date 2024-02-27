# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Augustin Borsu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Allow negative total in invoice",
    "summary": """
        Allow validating an invoice with a negative total amount
             """,
    "author": """
        Beescoop - Cellule IT,
        Coop IT Easy SCRLfs,
        Odoo Community Association (OCA)
    """,
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account Module",
    "version": "12.0.1.1.0",
    "depends": ["account"],
    "data": [
        "security/invoice_security.xml",
        "views/res_config_view.xml",
    ],
    "license": "AGPL-3",
}
