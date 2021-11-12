This module extends Stock Picking Invoicing implementation to Sale, you can define the 'Sale Invoicing Policy':

* If set to Sale Order, keep native Odoo behaviour for creation of invoices from Sale Orders.

* If set to Stock Picking, disallow creation of Invoices from Sale Orders for the cases where the Product Type are 'Product', in case of 'Service' still will be possible create from Sale Order.

For stock.moves, override price calculation that is present in stock_picking_invoicing, with the native Sale Order Line price calculation, same for the partner_id and other informations used to create the Invoice from Sale Order as such Payment Terms, Down Payments, Incoterm, Client Ref,etc by using sale methods to get data in order to avoid the necessity of 'glue modules' (small modules made just to avoid indirect dependencies), so in the case of any module include a new field in Invoice created by Sale this field also be include when created by Picking, for example the modules `Account Payment Sale`_  and `Sale Commission`_.

.. _`Account Payment Sale`: https://github.com/OCA/bank-payment/tree/14.0/account_payment_sale
.. _`Sale Commission`: https://github.com/OCA/commission/tree/14.0/sale_commission
