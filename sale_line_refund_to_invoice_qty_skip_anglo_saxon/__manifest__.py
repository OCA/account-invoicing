# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.
{
    "name": "Sale Line Refund To Invoice Qty Skip Anglo Saxon",
    "version": "15.0.1.0.0",
    "summary": "Sale Line Refund To Invoice Qty skip anglo saxon.",
    "category": "Accounting",
    "author": "ForgeFlow S.L, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "data": [
        "wizard/account_move_reversal_view.xml",
    ],
    "depends": [
        "account_invoice_refund_reason_skip_anglo_saxon",
        "sale_line_refund_to_invoice_qty",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["ChrisOForgeFlow"],
    "installable": True,
    "auto_install": True,
}
