# Configuration Guide

## Core Setup

### 1. Journal Configuration
**Path:** `Accounting → Configuration → Journals`  
**For new journal:**
1. Create → Type: Miscellaneous
2. Name: "Advance Compensation"
3. Code: ADV
4. Default Account: [Select prepayment account]
5. Advanced Settings → ☑ **Is Advance Journal**

### 2. Prepayment Accounts
**Path:** `Accounting → Configuration → Chart of Accounts`  
- **Customer Advances**:
  - Type: Current Assets
  - Name: "Advances Receivable"
  - ☑ Allow Reconciliation
- **Supplier Advances**:
  - Type: Current Liabilities
  - Name: "Advances Payable" 
  - ☑ Allow Reconciliation

### 3. Advance Product
**Path:** `Inventory → Products`  
- Name: "Advance Payment"
- Type: Service
- Accounting:
  - Income/Expense: [Linked to prepayment account]