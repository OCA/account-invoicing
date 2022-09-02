# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .test_account_move_post_block import TestAccountMovePostBlock


class TestAmPostBlockReason(TestAccountMovePostBlock):
    def test_am_post_block_manual_release(self):
        """Confirming the Blocked AM"""
        # Create an AM
        account_move = self._create_account_move(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        account_move.post_block_id = self.am_post_block_reason.id

        self.assertEqual(account_move.post_blocked, True)
        # The account manager unblocks the journal entry with block
        account_move.with_user(self.user2_id).button_release_post_block()
        self.assertEqual(
            account_move.post_block_id, self.env["account.post.block.reason"]
        )
        # The account user validates the journal entry without block
        account_move.with_user(self.user1_id).action_post()
        # The AM is posted
        self.assertEqual(account_move.state, "posted")

    def test_am_post_block_draft_release_01(self):
        # Create an AM
        account_move = self._create_account_move(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        account_move.post_block_id = self.am_post_block_reason.id
        self.assertEqual(account_move.state, "draft")

        # Simulation the opening of the wizard account_exception_confirm and
        # set ignore_exception to True
        ctx = {
            "active_id": account_move.id,
            "active_ids": [account_move.id],
            "active_model": account_move._name,
        }
        am_except_confirm = (
            self.env["account.exception.confirm"]
            .with_context(**ctx)
            .create({"ignore": True})
        )
        am_except_confirm.action_confirm()

        self.assertEqual(account_move.state, "posted")
