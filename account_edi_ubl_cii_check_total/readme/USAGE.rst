When importing a supplier invoice in UBL format, this module automatically
reads the total amount from the XML file and fills it into the Check Total field.

The module will:

- Extract the TaxInclusiveAmount from the UBL document.
- Automatically populate the Supplier’s Check Total field on the imported vendor bill.
- Allow users to easily compare the imported total with Odoo’s computed total to detect inconsistencies.