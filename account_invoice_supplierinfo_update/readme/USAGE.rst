This module adds a new button 'Check Supplier Info' in supplier
invoice form.

.. image:: ../static/description/supplier_invoice_form.png

When the user clicks on it, they can see the changes that will apply to the
vendor information. Optionally, they can remove some temporary changes,
specially, if, for example, a vendor applied an exceptional price change.

.. image:: ../static/description/main_screenshot.png

* blue: Creates a full new supplier info line
* brown: Updates current settings, displaying price variation (%)

This module adds an extra boolean field 'Supplier Informations Checked' in the
'Other Info' tab inside the supplier invoice form.
This field indicates that the prices have been checked and
supplierinfo updated (or eventually that the changes have been ignored).

.. image:: ../static/description/supplier_invoice_form_other_info_tab.png
