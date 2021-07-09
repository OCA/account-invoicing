Enable the option for multiple currencies in your instance:

#. Go to Invoicing > Configuration > Settings > Currencies > Multi-Currencies
#. Go to any draft invoice
#. Change the invoice currency
#. The proper currency rate, based on the invoice date and the selected currency, will be shown.
#. Add any invoice line.
#. Odoo has already generated the journal item lines with the rate applied, so the currency rate shown is get from the division between the amount in currency by the amount in company currency.

Some rates must be defined (and be distinct to 1.0) for currencies different from the company default.

#. Go to Invoicing > Configuration > Currencies and go to EUR
#. Go to Rates smart-button
#. Update 01/01/2010 record and change rate to 1.5
