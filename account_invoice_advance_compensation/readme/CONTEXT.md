# Module Context and Implementation Guide

## When to Use This Module

This module is particularly valuable for businesses that:

- Regularly process advance payments from customers or to suppliers
- Need to track prepayments separately from regular invoices
- Require precise reconciliation of advances against final invoices
- Operate in project-based or milestone-payment environments

## Key Implementation Scenarios

### Customer Advances
1. **Service Retainers**  
   - Track client deposits against monthly service invoices
   - Example: Law firm applying retainer payments to monthly bills

2. **Product Deposits**  
   - Manage customer down payments for goods
   - Example: Manufacturer applying 30% deposit against production order

### Supplier Prepayments
1. **Material Purchases**  
   - Track and apply prepayments to supplier invoices
   - Example: Construction company managing material prepayments

2. **Service Contracts**  
   - Reconcile advance payments to contractors
   - Example: IT firm managing vendor retainers

## Technical Context

### Prerequisites
- Odoo Accounting module installed
- Properly configured Chart of Accounts
- At least one journal marked as "Advance Journal"

### Integration Points
- Works with standard Odoo invoicing workflow
- Extends the account.move model
- Compatible with:
  - Odoo's native multi-currency
  - Multi-company setups
  - Standard reporting features
