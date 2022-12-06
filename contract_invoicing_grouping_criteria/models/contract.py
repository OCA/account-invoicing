from itertools import groupby

from odoo import models


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


def group(items, keys):
    """Group items by keys"""
    if not keys:
        return [(None, items)]

    grouping_keys = tuple(
        field if isinstance(field, str) else field.name for field in keys
    )
    return groupby(
        items.sorted(group_on_keys(grouping_keys, True)),
        key=group_on_keys(grouping_keys),
    )


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _get_base_invoice_grouping_keys(self):
        return ["company_id", "invoice_partner_id||partner_id", "currency_id"]

    def _merge_invoice_vals(self, invoices_vals, invoice_line_ids=None):
        """
        Merge several invoice vals into one containing all their invoice_line_ids
        or the one specified as argument if any
        """
        ref_invoice_vals = dict(invoices_vals[0])
        # Merge origins
        ref_invoice_vals["invoice_origin"] = ", ".join(
            list(
                dict.fromkeys(
                    invoice_vals["invoice_origin"] for invoice_vals in invoices_vals
                )
            )
        )
        # Merge references
        ref_invoice_vals["ref"] = ", ".join(
            list(
                dict.fromkeys(
                    invoice_vals["ref"]
                    for invoice_vals in invoices_vals
                    if invoice_vals["ref"]
                )
            )
        )[:2000]
        # Merge invoice_line_ids if not specified
        ref_invoice_vals["invoice_line_ids"] = invoice_line_ids or [
            invoice_line_ids
            for invoice_vals in invoices_vals
            for invoice_line_ids in invoice_vals["invoice_line_ids"]
        ]
        return ref_invoice_vals

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """Allow invoice groupping"""
        invoice_values = []
        # We need to group at least by company, partner and currency
        # To see if we have a grouping criteria for the contracts

        # Group contract by base criteria
        for base_group, base_contracts in group(
            self, self._get_base_invoice_grouping_keys()
        ):
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
            # NB: if there is no fields_ids we consider it as a single group
            for _, grouped_contracts in group(contracts, criteria.field_ids):
                # We convert the grouped_contract back to a recordset
                contracts = self.env["contract.contract"].browse(
                    c.id for c in grouped_contracts
                )

                # We can now prepare the grouped contract invoices
                grouped_invoice_vals = super(
                    ContractContract, contracts
                )._prepare_recurring_invoices_values(date_ref)

                # If there is no invoice_vals we can skip this group
                if not grouped_invoice_vals:
                    continue

                # Now we have to merge the invoices lines together if we have
                # a line grouping criteria
                if criteria.line_field_ids:
                    # Get invoice lines' contract lines to group them
                    contract_line_id_invoice_line_ids = {}
                    for invoice_vals in grouped_invoice_vals:
                        for _, _, line_vals in invoice_vals["invoice_line_ids"]:
                            contract_line_id_invoice_line_ids[
                                line_vals["contract_line_id"]
                            ] = line_vals

                    contract_lines = self.env["contract.line"].browse(
                        contract_line_id_invoice_line_ids.keys()
                    )
                    # We have line_field_ids, so we group contract lines by them
                    for _, grouped_contract_lines in group(
                        contract_lines, criteria.line_field_ids
                    ):
                        # We get the invoice lines back for this group
                        invoice_line_ids = [
                            contract_line_id_invoice_line_ids[contract_line.id]
                            for contract_line in grouped_contract_lines
                        ]

                        # Find the original invoices
                        original_invoices_vals = [
                            invoice_vals
                            for invoice_vals in grouped_invoice_vals
                            if any(
                                invoice_line_id
                                in [
                                    invoice_vals_line_ids
                                    for _, _, invoice_vals_line_ids in invoice_vals[
                                        "invoice_line_ids"
                                    ]
                                ]
                                for invoice_line_id in invoice_line_ids
                            )
                        ]

                        # Merge the original invoices
                        invoice_values.append(
                            self._merge_invoice_vals(
                                original_invoices_vals, invoice_line_ids
                            )
                        )

                else:
                    # Group contracts with the same criteria
                    # We use a similar algorithm as in the one in sale.order
                    invoice_values.append(
                        self._merge_invoice_vals(
                            grouped_invoice_vals,
                        )
                    )

        return invoice_values
