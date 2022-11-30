from odoo import models
from itertools import groupby


def group_on_keys(keys, get_ids=False):
    """Return a grouping function on the given keys"""

    def id_if_is_record(x):
        # if x is a record, return its id to get a consistent sorting
        return x.id if isinstance(x, models.BaseModel) else x

    def get_with_or(x, key):
        """Get key from x. Handles keys containing ||"""
        for k in key.split("||"):
            val = getattr(x, k)
            if val:
                return val
        return val

    get = (
        (lambda x, key: id_if_is_record(get_with_or(x, key)))
        if get_ids
        else get_with_or
    )

    def group_key(x):
        return tuple(get(x, key) for key in keys)

    return group_key


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _get_base_invoice_grouping_keys(self):
        return ["company_id", "invoice_partner_id||partner_id", "currency_id"]

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """Allow invoice groupping"""
        invoice_values = []

        # Group contract by base criteria
        base_grouping_keys = self._get_base_invoice_grouping_keys()
        base_contracts = self.sorted(group_on_keys(base_grouping_keys, True))
        base_contracts = groupby(base_contracts, key=group_on_keys(base_grouping_keys))

        for base_group, base_contracts in base_contracts:
            company, partner, *_ = base_group
            contracts = self.env["contract.contract"].browse(
                c.id for c in base_contracts
            )

            # Now we check if we have a grouping criteria:
            criteria = (
                partner.contract_invoicing_grouping_criteria_id
                or company.default_contract_invoicing_grouping_criteria_id
            )

            # If there are no criteria, we just keep the invoices as is
            if not criteria:
                invoice_values.extend(
                    super(
                        ContractContract, contracts
                    )._prepare_recurring_invoices_values(date_ref)
                )
                continue

            # We have a grouping criteria, so we regroup the contracts accordingly
            grouping_keys = tuple(field.name for field in criteria.field_ids)
            contracts = contracts.sorted(group_on_keys(grouping_keys, True))
            for _, grouped_contracts in groupby(
                contracts, key=group_on_keys(grouping_keys)
            ):
                contracts = self.env["contract.contract"].browse(
                    c.id for c in grouped_contracts
                )

                grouped_invoice_vals = super(
                    ContractContract, contracts
                )._prepare_recurring_invoices_values(date_ref)

                if not grouped_invoice_vals:
                    continue

                # We use a similar algorithm as in the one in sale.order
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in grouped_invoice_vals:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals["invoice_line_ids"] += invoice_vals[
                            "invoice_line_ids"
                        ]
                    origins.add(invoice_vals["invoice_origin"])
                    payment_refs.add(invoice_vals["payment_reference"])
                    refs.add(invoice_vals["ref"] or "")

                ref_invoice_vals.update(
                    {
                        "ref": ", ".join(refs)[:2000],
                        "invoice_origin": ", ".join(origins),
                        "payment_reference": len(payment_refs) == 1
                        and payment_refs.pop()
                        or False,
                    }
                )
                invoice_values.append(ref_invoice_vals)

        return invoice_values
