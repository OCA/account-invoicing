Odoo ``account`` module displays discounts on invoice lines only if ``sale``
module is installed, that is bad designed. (To see discount, user should
be member of ``sale.group_discount_per_so_line``)
For that reason, this module depends on ``sale`` module.
This dependency should be removed in more recent version if the design of
Odoo is improved.
