# Copyright 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Account Analytic Billing Plan",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Accounting & Finance",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/account_analytic_account_view.xml",
        "views/account_analytic_billing_plan_view.xml",
    ],
    "installable": True,
}
