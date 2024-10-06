{
    "name": "Account Move Tag",
    "summary": """
        Adds tags to the account move so vendor bills and customer invoices can be
        easily distinguished in the accounting journal.
    """,
    "author": "Codeforward B.V., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Hidden",
    "version": "17.0.1.0.0",
    "depends": ["account"],
    "license": "LGPL-3",
    "data": [
        "views/account_move_views.xml",
        "views/account_move_line_views.xml",
        "views/account_move_tag_views.xml",
        "views/account_move_tag_menu_views.xml",
        "security/ir.model.access.csv",
    ],
}
