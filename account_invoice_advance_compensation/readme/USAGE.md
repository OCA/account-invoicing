This module allows you to manage advance payments and their compensation against regular invoices. It supports both customer and supplier invoices, with multi-currency capabilities.

## Step-by-Step Process

### 1. Recording an Advance Payment
1. Create a new invoice with the "Advance" product
2. Register the complete payment for the advance invoice
3. The advance will be available for compensation once fully paid

### 2. Applying Compensation
1. Open the regular invoice (must be for the same partner)
2. Click the **Compensate Advance** button
3. In the compensation wizard:
   - Select available advance(s) from the left panel
   - Choose invoice lines to compensate on the right
   - Enter the compensation amount
4. Click **Compensate** to apply the compensation

## Key Features

### Supported Scenarios
- Customer and supplier invoices
- Partial compensation of advances
- Multi-currency transactions
- Multiple advance compensations per invoice

### Prerequisites
- Advance invoice must be fully paid
- Regular invoice must be for the same partner
- Accounts must be reconcilable
- Proper journal configuration

## Troubleshooting

### Common Issues
1. **Advance not appearing in compensation wizard**
   - Verify the advance invoice is fully paid
   - Check if the partner matches
   - Confirm journal settings are correct

2. **Compensation not working**
   - Ensure accounts are properly configured
   - Check currency compatibility
   - Verify user has necessary permissions
