This module is useful when the `invoice_date` of a customer invoice needs to reflect a  
specific operational date from the related delivery order.

One example of such an implementation case is as follows:

- Install OCA modules sale_automatic_wofklow and stock_move_actual_date, along with this module.
- Select the actual date field as the Picking Date Field for Invoice Date.
- Configure automatic workflow domain so that the delivery is validated and the invoice is created when the date
  set in the actual date has arrived.
