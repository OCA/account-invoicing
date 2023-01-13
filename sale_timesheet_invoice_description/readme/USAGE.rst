To use this module, you need to:

#. Create or modify a product and set the following options under
   'General Information' tab:

   - **Product Type** > 'Service'
   - **Invoicing Policy** > 'Based on Timesheets'
   - **Create on Order** > 'Project & Task'
   - **Unit of Measure** > 'Hours' (or any other time unit)
#. Go to *Sales > Orders > Orders*, select a Sale Order or create a new one,
   add a product (service) under 'Order Lines' tab.
#. Go to 'Other Info' tab (within the same Sale Order) and:

   - Select an option from **Timesheet Invoice Description**.
   - For **Split Order lines by** select "Timesheet" if you want to create one
     invoice line for each Sale Order line's timesheet, or select "Task" if you
     want to create one invoice line for each Sale Order line's task.
   - For **Timesheets for consecutive Invoices** select "Only uninvoiced" if
     you want to ignore all already fully or partially invoiced timesheets when
     creating consecutive invoices, or select "Uninvoiced and partially
     invoiced" if you want to ignore only the already fully invoiced
     timesheets.

     - Caveat: Since a timesheet can be linked to only a single invoice line
       (by its fields "Invoice Line"), the option "Uninvoiced and partially
       invoiced" works for partially invoiced timesheets only on a second
       invoice. The timesheet will then be linked to (only) its new invoice
       line, and thus any further invoices are unable to determine the not yet
       invoiced amount of that timesheet, because the link to the line on the
       first invoice is no longer known.

   - Link the Sale Order with a project from **Project** field.
#. Confirm Sale.
#. Go to *Timesheets > Timesheets > My Timesheets*, create a record
   (timesheet line) and select a task related to the Sale Order's project
   (and to your specific Sale Order's line). Remember to add the time spent.
#. Go to the Sale Order and create its invoice (click on 'Create Invoice').
