import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_invoice_blocking',
        'odoo9-addon-account_invoice_check_total',
        'odoo9-addon-account_invoice_fiscal_position_update',
        'odoo9-addon-account_invoice_fixed_discount',
        'odoo9-addon-account_invoice_line_sequence',
        'odoo9-addon-account_invoice_merge',
        'odoo9-addon-account_invoice_merge_payment',
        'odoo9-addon-account_invoice_merge_purchase',
        'odoo9-addon-account_invoice_pricelist',
        'odoo9-addon-account_invoice_refund_link',
        'odoo9-addon-account_invoice_refund_option',
        'odoo9-addon-account_invoice_rounding',
        'odoo9-addon-account_invoice_search_by_reference',
        'odoo9-addon-account_invoice_supplier_ref_unique',
        'odoo9-addon-account_invoice_view_payment',
        'odoo9-addon-account_payment_term_extension',
        'odoo9-addon-purchase_batch_invoicing',
        'odoo9-addon-purchase_stock_picking_return_invoicing',
        'odoo9-addon-purchase_stock_picking_return_invoicing_open_qty',
        'odoo9-addon-sale_stock_picking_return_invoicing',
        'odoo9-addon-sale_timesheet_invoice_description',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
