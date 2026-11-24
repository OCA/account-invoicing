// Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {accountTaxHelpers} from "@account/helpers/account_tax";
import {patch} from "@web/core/utils/patch";

patch(accountTaxHelpers, {
    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    add_tax_details_in_base_line(base_line, company, kwargs) {
        this._document_currency_id = base_line.currency_id?.id;
        this._document_rate = base_line.rate || 1.0;
        try {
            return super.add_tax_details_in_base_line(base_line, company, kwargs);
        } finally {
            delete this._document_currency_id;
            delete this._document_rate;
        }
    },

    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    _eval_tax_amount_convert_currency(tax, amount) {
        // When called outside a document context, no conversion to apply
        if (!this._document_currency_id) {
            return amount;
        }
        // If the currency already matches, skip the conversion
        if (tax.currency_id === this._document_currency_id) {
            return amount;
        }
        // Convert: tax currency → company currency → document currency
        return amount * tax.currency_rate * this._document_rate;
    },

    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    // eslint-disable-next-line no-unused-vars
    eval_tax_amount_fixed_amount(tax, batch, raw_base, evaluation_context) {
        const res = super.eval_tax_amount_fixed_amount(...arguments);
        if (tax.amount_type === "fixed" && tax.currency_id) {
            return this._eval_tax_amount_convert_currency(tax, res);
        }
        return res;
    },
});
