import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_invoice_blocking>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_check_total>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_fiscal_position_update>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_merge>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_refund_link>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_tax_required>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_transmit_method>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_triple_discount>=16.0dev,<16.1dev',
        'odoo-addon-account_menu_invoice_refund>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
