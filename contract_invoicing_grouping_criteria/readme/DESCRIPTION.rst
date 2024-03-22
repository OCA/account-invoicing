
This module allows to group invoicing of several contracts and to use custom
criteria for grouping contracts to be invoiced.

This module mimics the sale.order grouping behavior of the sale module and adds
the sale_order_invoicing_grouping_criteria's custom criteria mechanism.

Default criteria for grouping (invoicing partner, company and used currency)
will be always applied, as if not respected, there will be business
inconsistencies, but you can add more fields to split the invoicing according
them.
