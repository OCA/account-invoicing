# -*- coding: utf-8 -*-

{
    'name': 'Order to Invoice by Percent',
    'version': '1.0',
    'author': 'Ecosoft',
    'category': 'Sales',
    'description': """

This module enhance the existing Create Invoice (Advance / Percentage)
concept of standard Odoo by 2 things,

Create Invoice by Percent
=========================

Ability to create invoice by percentage of completion. This is not the same as
existing "Percentage" method that using the whole net amount, instead,
it goes into each line of Sales Order to create new Invoice.

This result a real create invoice by percentage of completion.

In addition, it also allow user to use Amount instead of percent
(system will do the convert to percent).

1st Deposit Invoice
===================

Only on the first invoice creation from a sales order, user can choose
to create a Deposit, by percent or by amount.

The created invoice will be using default Deposit Account Code from
Account Configuration, and thus post account correctly.

On the following invoice creation, no more deposit can be created,
but rather a whole invoice or percent of completion.
The 1st deposit amount will then be deducted on the following invoices,
evenly by percentage of the invoice amount.

    """,
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['sale',
                'purchase',
                'sale_order_action_invoice_create_hooks',
                'sale_order_make_invoice_hooks',
                'sale_wizard_make_invoices_hooks',
                ],
    'demo': [],
    'data': ['wizards/sale_make_invoice_advance.xml',
             'wizards/purchase_make_invoice_advance.xml',
             'views/sale_view.xml',
             'views/purchase_view.xml',
             'views/account_invoice_view.xml',
             'views/res_config_view.xml',
             'data/sale_workflow.xml', ],
    'test': [],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
