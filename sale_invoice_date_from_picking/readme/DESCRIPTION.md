This module sets the invoice date based on the date or datetime field configured in the
'Picking Date for Invoice' setting, and the accounting date based on the field configured
in the 'Picking Date for Accounting Date' setting. If the selected field has no value, the
system will fallback to using the `date_done` of the latest completed picking.
