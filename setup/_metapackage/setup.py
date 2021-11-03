import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-invoicing",
    description="Meta package for oca-account-invoicing Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_billing',
        'odoo14-addon-account_invoice_base_invoicing_mode',
        'odoo14-addon-account_invoice_check_total',
        'odoo14-addon-account_invoice_date_due',
        'odoo14-addon-account_invoice_force_number',
        'odoo14-addon-account_invoice_mode_at_shipping',
        'odoo14-addon-account_invoice_mode_monthly',
        'odoo14-addon-account_invoice_mode_weekly',
        'odoo14-addon-account_invoice_payment_retention',
        'odoo14-addon-account_invoice_refund_link',
        'odoo14-addon-account_invoice_restrict_linked_so',
        'odoo14-addon-account_invoice_search_by_reference',
        'odoo14-addon-account_invoice_section_sale_order',
        'odoo14-addon-account_invoice_supplier_ref_unique',
        'odoo14-addon-account_invoice_tax_required',
        'odoo14-addon-account_invoice_transmit_method',
        'odoo14-addon-account_invoice_tree_currency',
        'odoo14-addon-account_invoice_triple_discount',
        'odoo14-addon-account_move_original_partner',
        'odoo14-addon-account_move_tier_validation',
        'odoo14-addon-product_supplierinfo_for_customer_invoice',
        'odoo14-addon-purchase_stock_picking_return_invoicing',
        'odoo14-addon-sale_order_invoicing_grouping_criteria',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
