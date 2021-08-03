# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Customer code for account invoice",
    "summary": "Based on product_customer_code, this module loads in every "
    "account invoice the customer code defined in the product",
    "version": "14.0.1.0.0",
    "author": "Agile Business Group, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account",
    "license": "AGPL-3",
    "depends": ["account", "product_supplierinfo_for_customer"],
    "data": ["views/account_move_view.xml"],
    "installable": True,
}
