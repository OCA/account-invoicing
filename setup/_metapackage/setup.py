import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_invoice_change_currency>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_check_total>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_date_due>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_fiscal_position_update>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_refund_link>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_search_by_reference>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_tax_note>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_tax_required>=15.0dev,<15.1dev',
        'odoo-addon-account_invoice_tree_currency>=15.0dev,<15.1dev',
        'odoo-addon-account_move_tier_validation>=15.0dev,<15.1dev',
        'odoo-addon-sale_order_invoicing_grouping_criteria>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
