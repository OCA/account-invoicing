{
    "name": "Account line product name visibility",
    "version": "20.0.1.0.0",
    "summary": "Hide product name on invoice lines",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_line_views.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "maintainers": ["Andrii9090-tecnativa"],
    "post_init_hook": "post_init_hook",
}
