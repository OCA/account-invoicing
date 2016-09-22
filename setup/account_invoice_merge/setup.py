import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    install_requires=[
        'odoo8-addon-account_invoice_merge_purchase',
        'odoo8-addon-account_invoice_merge_payment',
    ],
    odoo_addon=True,
)
