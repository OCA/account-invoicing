**Business need:** In previous Odoo versions, users could create a vendor bill directly from a purchase order with a single click using a dedicated button in the form header. Starting from Odoo v19, this button was removed from the core `purchase` module, forcing users to directly upload the invoice file.

**Approach:** This module adds back the "Create Bill" button in the purchase order form by inheriting the `purchase.purchase_order_form` view and inserting the button in the same position, right after the existing action buttons. It respects the same visibility conditions based on the order state and invoice status.

**Useful information:** This module only depends on the core `purchase` module, making it lightweight and easy to install. It is compatible with any other module that extends purchase order functionality.
