# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveTag(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = cls.env["account.move.tag"].create({"name": "Test Tag"})

    def test_default_color(self):
        self.assertTrue(1 <= self.tag.color <= 11)

    def test_unique_name(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self.env["account.move.tag"].create({"name": "Test Tag"})

    def test_tags_on_move_and_lines(self):
        move = self.init_invoice("out_invoice", amounts=[100.0])
        move.tag_ids = self.tag
        self.assertEqual(move.line_ids.tag_ids, self.tag)
        self.assertEqual(
            self.env["account.move"].search([("tag_ids", "=", self.tag.id)]), move
        )
