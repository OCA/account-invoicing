To use this module:

1. Go to **Contacts** or **Invoicing > Customers > Customers** and select a customer.
2. In the **Invoicing** tab under **Customer Invoices**, locate the **Invoice Recipients** field.
3. Select the additional partner contacts (e.g., Accounts Payable, billing managers) who should receive invoices. Ensure these contacts have valid email addresses.
4. When creating a customer invoice for this partner, the **Invoice Recipients** field under **Other Info** is automatically populated. You can add or remove recipients on the draft invoice if needed.
5. Send the invoice:
   * **Single send**: Click **Send & Print**. The "To" field in the sending wizard is automatically pre-filled with the customer and all configured recipients.
   * **Batch send**: Select multiple invoices in the list view and click **Send & Print**. Each invoice will be emailed to its primary customer plus all configured invoice recipients.
   * **Automated sending**: If automated sending is enabled (e.g., via `account_invoice_auto_send_by_email`), the background job will dispatch the invoice to all configured recipients.
