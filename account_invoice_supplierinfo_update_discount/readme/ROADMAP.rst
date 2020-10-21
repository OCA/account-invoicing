Odoo ``account`` module displays discounts on invoice lines only if ``sale``
module is installed, that is bad design. To avoid useless dependencies, this
module does not depend on sale module, and so, displays allways discount
features, even if the user doesn't belong to the group 
``sale.group_discount_per_so_line``.
