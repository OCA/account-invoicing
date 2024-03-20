Enable the option for multiple currencies in your instance:

1.  Go to Invoicing \> Configuration \> Settings \> Currencies \>
    Multi-Currencies
2.  Go to any draft invoice
3.  Change the invoice currency
4.  The proper currency rate, based on the invoice date and the selected
    currency, will be shown.
5.  Add any invoice line.
6.  Odoo has already generated the journal item lines with the rate
    applied, so the currency rate shown is get from the division between
    the amount in currency by the amount in company currency.

Some rates must be defined (and be distinct to 1.0) for currencies
different from the company default.

1.  Go to Invoicing \> Configuration \> Currencies and go to EUR
2.  Go to Rates smart-button
3.  Update 01/01/2010 record and change rate to 1.5
