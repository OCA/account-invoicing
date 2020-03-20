import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_invoice_fixed_discount',
        'odoo13-addon-account_invoice_force_number',
        'odoo13-addon-account_invoice_refund_link',
        'odoo13-addon-account_invoice_search_by_reference',
        'odoo13-addon-account_invoice_supplier_ref_reuse',
        'odoo13-addon-account_invoice_supplier_ref_unique',
        'odoo13-addon-account_move_tier_validation',
        'odoo13-addon-sale_order_invoicing_grouping_criteria',
        'odoo13-addon-sale_order_invoicing_queued',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
