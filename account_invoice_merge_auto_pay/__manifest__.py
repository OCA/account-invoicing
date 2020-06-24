# coding: utf-8
# Copyright (C) 2019 - Today: Commown (https://commown.coop)
# @author: Florent Cayré
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account invoice merge auto pay',
    'category': 'accounting',
    'version': '10.0.0.0.4',
    'author': "Commown SCIC SAS",
    'license': "AGPL-3",
    'website': "https://commown.coop",

    'external_dependencies': {
        # 'python': []
    },

    'depends': [
        'account_invoice_merge_auto',
        'account_payment_partner',  # payment_mode_id on account.invoice
        'contract_payment_auto',    # payment_token_id on res.partner
        'queue_job_subscribe',
    ],

    'data': [
    ],

    'installable': True,
    'application': False,
}
