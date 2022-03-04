# coding: utf-8
# Copyright (C) 2019 - Today: Commown (https://commown.coop)
# @author: Florent Cayré
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account invoice merge auto pay",
    "category": "accounting",
    "version": "12.0.1.0.0",
    "author": "Commown SCIC SAS",
    "license": "AGPL-3",
    "website": "https://commown.coop",

    "depends": [
        "account_invoice_merge_auto",
        "contract_payment_auto",
        "queue_job",        
    ],
    "installable": True,
}
