from . import models
from openupgradelib import openupgrade


def rename_old_italian_data(cr):

    if not openupgrade.is_module_installed(cr, "l10n_it_corrispettivi"):
        return

    openupgrade.rename_xmlids(
        cr,
        [
            (
                "l10n_it_corrispettivi.corrispettivi_journal",
                "account_receipt_journal.sale_receipts_journal",
            ),
        ],
    )
