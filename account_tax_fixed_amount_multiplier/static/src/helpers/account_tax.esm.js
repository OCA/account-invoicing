// Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {accountTaxHelpers} from "@account/helpers/account_tax";
import {patch} from "@web/core/utils/patch";

patch(accountTaxHelpers, {
    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    _get_fixed_amount_product_quantity(evaluation_context) {
        const quantity = evaluation_context.quantity;
        const uom_factor = evaluation_context.uom.factor || 1.0;
        const product_uom_factor = evaluation_context.product.uom_factor || 1.0;
        return (quantity * uom_factor) / product_uom_factor;
    },

    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    _get_fixed_amount_quantity(tax, evaluation_context) {
        if (tax.fixed_amount_multiplier === "none") {
            return 1.0;
        } else if (tax.fixed_amount_multiplier === "product_quantity") {
            return this._get_fixed_amount_product_quantity(evaluation_context);
        } else if (tax.fixed_amount_multiplier === "product_weight") {
            const quantity =
                this._get_fixed_amount_product_quantity(evaluation_context);
            return quantity * (evaluation_context.product.weight || 0.0);
        }
        return evaluation_context.quantity;
    },

    /**
     * [!] Mirror of the same method in account_tax.py.
     * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
     */
    eval_tax_amount_fixed_amount(tax, batch, raw_base, evaluation_context) {
        if (tax.amount_type === "fixed" && tax.fixed_amount_multiplier !== "quantity") {
            const quantity = this._get_fixed_amount_quantity(tax, evaluation_context);
            const multiplierEvaluationContext = {
                ...evaluation_context,
                quantity,
            };
            return super.eval_tax_amount_fixed_amount(
                tax,
                batch,
                raw_base,
                multiplierEvaluationContext
            );
        }
        return super.eval_tax_amount_fixed_amount(
            tax,
            batch,
            raw_base,
            evaluation_context
        );
    },
});
