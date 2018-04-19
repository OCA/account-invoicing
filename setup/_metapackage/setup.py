import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_group_invoice_lines',
        'odoo8-addon-account_invoice_force_number',
        'odoo8-addon-account_invoice_kanban',
        'odoo8-addon-account_invoice_line_description',
        'odoo8-addon-account_invoice_line_price_subtotal_gross',
        'odoo8-addon-account_invoice_line_sort',
        'odoo8-addon-account_invoice_merge',
        'odoo8-addon-account_invoice_merge_payment',
        'odoo8-addon-account_invoice_merge_purchase',
        'odoo8-addon-account_invoice_partner',
        'odoo8-addon-account_invoice_period_usability',
        'odoo8-addon-account_invoice_pricelist',
        'odoo8-addon-account_invoice_pricelist_sale',
        'odoo8-addon-account_invoice_pricelist_sale_stock',
        'odoo8-addon-account_invoice_rounding',
        'odoo8-addon-account_invoice_rounding_by_currency',
        'odoo8-addon-account_invoice_shipping_address',
        'odoo8-addon-account_invoice_supplier_number_info',
        'odoo8-addon-account_invoice_supplier_ref_unique',
        'odoo8-addon-account_invoice_supplierinfo_update',
        'odoo8-addon-account_invoice_supplierinfo_update_discount',
        'odoo8-addon-account_invoice_supplierinfo_update_on_validate',
        'odoo8-addon-account_invoice_supplierinfo_update_variant',
        'odoo8-addon-account_invoice_transmit_method',
        'odoo8-addon-account_invoice_triple_discount',
        'odoo8-addon-account_invoice_uom',
        'odoo8-addon-account_invoice_validation_workflow',
        'odoo8-addon-account_invoice_zero_autopay',
        'odoo8-addon-account_payment_term_extension',
        'odoo8-addon-invoice_fiscal_position_update',
        'odoo8-addon-invoice_margin',
        'odoo8-addon-sale_order_line_price_subtotal_gross',
        'odoo8-addon-stock_picking_invoice_product_group',
        'odoo8-addon-stock_picking_invoicing_incoterm',
        'odoo8-addon-stock_picking_invoicing_incoterm_sale',
        'odoo8-addon-stock_picking_invoicing_unified',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
