# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Augustin Borsu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Invoice date required",
    "summary": """
        Makes date_invoice field required in account.invoice_form and
        account.invoice_supplier_form
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
        "views/account_invoice.xml",
    ],
    "license": "AGPL-3",
}
