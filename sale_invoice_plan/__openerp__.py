# -*- coding: utf-8 -*-

{
    'name': 'Sales - Invoice Planning',
    'version': '1.0',
    'author': 'Ecosoft',
    'category': 'Sales',
    'description': """

This module focus on business case when user know exactly how many invoice and
payment collection will be issued for a sales order in the future.

The module provide a wizard that allow user to decide number of installment,
date invoice and percentage of each installment.

The installment will be created in the product line detail level, allowing user
to edit amount/percentage of invoice in each product line separately.

In addition to the invoice plan, the 1st deposit invoice can also be created,
and will be deducted in percentage of invoice on following invoice.

This module is based on Adhoc 1st Deposit and Invoice by Percent,
and can be refer to, but in the "Planned" way.

Feature List
============

  * Sales Order, user can choose to use "Invoice Plan",
  a new tab "Invoice Plan" will be visible.
  * Using wizard, user can define number of installment,
  and whether it has deposit on the first installment.
  * A new Invoice Plan will be created with product line detail.
  User can choose to edit percentage/amount of each installment in more detail.
  * Validation will take place when the Sales Order is confirmed,
  make sure that, the sum amount of all installment is valid
  * User clicking on Create Invoice button, only option available
  is to "Invoice the whole sales order".
  * At one click, multiple invoice will be created,
  according to the invoice plan.
  * If 1st invoice is deposit, following invoice will be deducted accordingly.

    """,
    'website': 'www.ecosoft.co.th',
    'depends': ['order_invoice_line_percentage',
                'sale_order_line_prepare_order_line_invoice_line_hooks'],
    'data': [
        "wizard/sale_create_invoice_plan_view.xml",
        "sale_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
