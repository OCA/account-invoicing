# Copyright 2019 Simone Rubino

from odoo.addons.portal.controllers.portal import CustomerPortal


class CorrispettiviPortal(CustomerPortal):

    def _show_report(self, model, report_type, report_ref, download=False):
        if model._name == 'account.invoice' and model.corrispettivo:
            report_ref = 'l10n_it_corrispettivi.account_corrispettivi'
        return super()._show_report(model, report_type, report_ref, download)
