# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    xml_spec = []
    sale_journal_xmlid = "account_receipt_journal.sale_receipts_journal"
    purchase_journal_xmlid = "account_receipt_journal.purchase_receipts_journal"
    sale_journal = env.ref(sale_journal_xmlid, raise_if_not_found=False)
    purchase_journal = env.ref(purchase_journal_xmlid, raise_if_not_found=False)
    if sale_journal:
        xml_spec.append(
            (
                sale_journal_xmlid,
                f"account.{sale_journal.company_id.id}_sale_receipt_journal",
            )
        )
    if purchase_journal:
        xml_spec.append(
            (
                purchase_journal_xmlid,
                f"account.{purchase_journal.company_id.id}_purchase_receipts_journal",
            )
        )
    if xml_spec:
        openupgrade.rename_xmlids(env.cr, xml_spec)
