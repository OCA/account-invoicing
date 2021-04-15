import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_billing',
        'odoo14-addon-account_invoice_date_due',
        'odoo14-addon-account_invoice_refund_link',
        'odoo14-addon-account_invoice_search_by_reference',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
