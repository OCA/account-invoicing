#  Copyright 2021 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResCompany (models.Model):
    _inherit = 'res.company'

    @api.multi
    def _get_corrispettivi_partner(self):
        """
        Similar to res.company._get_public_user (website module),
        but creates a user for corrispettivi copied from the public user
        and returns the linked partner.
        """
        self.ensure_one()
        # We need sudo to be able to see public users from others companies too
        public_users = self.env.ref('base.group_public').sudo() \
            .with_context(active_test=False).users
        public_users_for_company = public_users.filtered(
            lambda user: user.company_id == self)

        if public_users_for_company:
            corrispettivi_user = public_users_for_company[0]
        else:
            corrispettivi_user = self.env.ref('base.public_user').sudo().copy({
                'name': 'Corrispettivi user for %s' % self.name,
                'login': 'corrispettivi-user@company-%s.com' % self.id,
                'company_id': self.id,
                'company_ids': [(6, 0, self.ids)],
            })
        return corrispettivi_user.partner_id
