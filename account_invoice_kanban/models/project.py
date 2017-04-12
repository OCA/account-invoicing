# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    used_in_invoice = fields.Boolean('Used in Invoicing')
