from . import models
from . import wizard
from openupgradelib import openupgrade


def rename_old_italian_module(cr):

    if not openupgrade.is_module_installed(cr, "l10n_it_corrispettivi"):
        return

    openupgrade.update_module_names(
        cr,
        [
            ("l10n_it_corrispettivi", "account_receipt_sale"),
        ],
        merge_modules=True,
    )

    if openupgrade.column_exists(
        cr, "account_move", "old_invoice_id"
    ) and openupgrade.column_exists(cr, "account_invoice", "corrispettivo"):
        # l10n_it_corrispettivi handled sale receipts only
        openupgrade.logged_query(
            cr,
            "UPDATE account_move m "
            "SET move_type = 'out_receipt' "
            "FROM account_invoice i "
            "WHERE i.corrispettivo = true AND i.id = m.old_invoice_id",
        )

    if openupgrade.column_exists(cr, "account_journal", "corrispettivi"):
        openupgrade.logged_query(
            cr,
            "UPDATE account_journal "
            "SET receipts = true "
            "WHERE corrispettivi = true",
        )

    if openupgrade.column_exists(cr, "account_fiscal_position", "corrispettivi"):
        openupgrade.logged_query(
            cr,
            "UPDATE account_fiscal_position "
            "SET receipts = true "
            "WHERE corrispettivi = true",
        )

    if openupgrade.column_exists(cr, "res_partner", "use_corrispettivi"):
        openupgrade.logged_query(
            cr,
            "UPDATE res_partner "
            "SET use_receipts = true "
            "WHERE use_corrispettivi = true",
        )

    if not openupgrade.is_module_installed(cr, "l10n_it_corrispettivi_sale"):
        return

    openupgrade.update_module_names(
        cr,
        [
            ("l10n_it_corrispettivi_sale", "account_receipt_sale"),
        ],
        merge_modules=True,
    )

    if openupgrade.column_exists(cr, "sale_order", "corrispettivi"):
        openupgrade.logged_query(
            cr,
            "UPDATE sale_order "
            "SET receipts = true "
            "WHERE corrispettivi = true",
        )
