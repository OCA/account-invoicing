from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class AccountingPartnerCategory(TransactionCase):
    def test_tag_unique(self):
        self.env["accounting.partner.category"].create({"name": "test"})

        with mute_logger("odoo.sql_db"):
            with self.assertRaisesRegex(
                IntegrityError, "accounting_partner_category_name_uniq"
            ):
                self.env["accounting.partner.category"].create({"name": "test"})
