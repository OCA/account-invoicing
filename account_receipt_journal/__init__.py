from . import models
from openupgradelib import openupgrade


def rename_old_italian_data(env):
    if not openupgrade.is_module_installed(env.cr, "l10n_it_corrispettivi"):
        return

    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "l10n_it_corrispettivi.corrispettivi_journal",
                "account_receipt_journal.sale_receipts_journal",
            ),
        ],
    )
