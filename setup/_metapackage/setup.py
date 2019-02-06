import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_invoice_change_currency',
        'odoo12-addon-account_invoice_check_total',
        'odoo12-addon-account_invoice_force_number',
        'odoo12-addon-account_invoice_line_description',
        'odoo12-addon-account_invoice_refund_link',
        'odoo12-addon-account_invoice_triple_discount',
        'odoo12-addon-sale_timesheet_invoice_description',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
