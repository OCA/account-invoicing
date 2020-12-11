# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountApprovalProcess(models.Model):
    _inherit = "account.approval.process"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        relation="account_approval_process_hr_department_rel",
        column1="approval_id",
        column2="department_id",
        string="Allowed Employees of departments",
    )

    manager_of_department_ids = fields.Many2many(
        comodel_name="hr.department",
        relation="account_approval_process_hr_department_manager_rel",
        column1="approval_id",
        column2="department_id",
        string="Allowed manager of departments",
    )

    def get_users_with_access_rights(self):
        users = super(AccountApprovalProcess, self).get_users_with_access_rights()

        for department in self.manager_of_department_ids:
            users |= department.manager_id.user_id

        for department in self.department_ids:
            for member in department.member_ids:
                users |= member.user_id

        return users

    def has_current_user_access_rights(self):
        res = super(AccountApprovalProcess, self).has_current_user_access_rights()
        if not res:
            users = self.env["res.users"]
            for department in self.manager_of_department_ids:
                users |= department.manager_id.user_id

            for department in self.department_ids:
                for member in department.member_ids:
                    users |= member.user_id

            res = self.env.user.id in users.ids

        return res
