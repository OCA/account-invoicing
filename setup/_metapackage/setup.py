import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-account_group_invoice_line',
        'odoo10-addon-account_invoice_analytic_search',
        'odoo10-addon-account_invoice_blocking',
        'odoo10-addon-account_invoice_change_currency',
        'odoo10-addon-account_invoice_check_total',
        'odoo10-addon-account_invoice_fiscal_position_update',
        'odoo10-addon-account_invoice_fixed_discount',
        'odoo10-addon-account_invoice_force_number',
        'odoo10-addon-account_invoice_kanban',
        'odoo10-addon-account_invoice_line_description',
        'odoo10-addon-account_invoice_line_sequence',
        'odoo10-addon-account_invoice_merge',
        'odoo10-addon-account_invoice_merge_attachment',
        'odoo10-addon-account_invoice_merge_payment',
        'odoo10-addon-account_invoice_merge_purchase',
        'odoo10-addon-account_invoice_partner',
        'odoo10-addon-account_invoice_pricelist',
        'odoo10-addon-account_invoice_pricelist_sale',
        'odoo10-addon-account_invoice_pro_forma_sequence',
        'odoo10-addon-account_invoice_refund_link',
        'odoo10-addon-account_invoice_rounding',
        'odoo10-addon-account_invoice_search_by_reference',
        'odoo10-addon-account_invoice_supplier_ref_unique',
        'odoo10-addon-account_invoice_supplierinfo_update',
        'odoo10-addon-account_invoice_transmit_method',
        'odoo10-addon-account_invoice_triple_discount',
        'odoo10-addon-account_invoice_view_payment',
        'odoo10-addon-account_payment_term_extension',
        'odoo10-addon-purchase_stock_picking_return_invoicing',
        'odoo10-addon-sale_timesheet_invoice_description',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
