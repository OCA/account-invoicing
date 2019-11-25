import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_invoice_analytic_search',
        'odoo12-addon-account_invoice_anglo_saxon_no_cogs_deferral',
        'odoo12-addon-account_invoice_blocking',
        'odoo12-addon-account_invoice_change_currency',
        'odoo12-addon-account_invoice_check_total',
        'odoo12-addon-account_invoice_fiscal_position_update',
        'odoo12-addon-account_invoice_fixed_discount',
        'odoo12-addon-account_invoice_force_number',
        'odoo12-addon-account_invoice_line_description',
        'odoo12-addon-account_invoice_line_sequence',
        'odoo12-addon-account_invoice_pricelist',
        'odoo12-addon-account_invoice_pricelist_sale',
        'odoo12-addon-account_invoice_refund_link',
        'odoo12-addon-account_invoice_reimbursable',
        'odoo12-addon-account_invoice_repair_link',
        'odoo12-addon-account_invoice_search_by_reference',
        'odoo12-addon-account_invoice_supplier_ref_reuse',
        'odoo12-addon-account_invoice_supplier_ref_unique',
        'odoo12-addon-account_invoice_supplierinfo_update',
        'odoo12-addon-account_invoice_tax_note',
        'odoo12-addon-account_invoice_tax_required',
        'odoo12-addon-account_invoice_transmit_method',
        'odoo12-addon-account_invoice_triple_discount',
        'odoo12-addon-account_invoice_validation_queued',
        'odoo12-addon-account_invoice_view_payment',
        'odoo12-addon-account_menu_invoice_refund',
        'odoo12-addon-account_payment_term_extension',
        'odoo12-addon-purchase_batch_invoicing',
        'odoo12-addon-purchase_stock_picking_return_invoicing',
        'odoo12-addon-purchase_stock_picking_return_invoicing_force_invoiced',
        'odoo12-addon-sale_invoice_line_note',
        'odoo12-addon-sale_order_invoicing_queued',
        'odoo12-addon-sale_timesheet_invoice_description',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
