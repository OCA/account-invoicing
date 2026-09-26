**Overview**
This module enforces strict security restrictions on financial documents (`account.move`) for users who should not have full accounting privileges.

**The Problem**
Certain standard or third-party addons (such as `purchase`) inadvertently grant full read/write/delete access to invoicing and journal entries, bypassing the intended restrictive business roles.

**The Solution**
This module overrides access control with `check_access()`. It ensures that:
* **Creation, Edition, and Deletion** on `account.move` are strictly blocked for users who are not part of the `account.group_account_invoice`.
* Users with Technical/Show Accounting Features - Readonly group or no Accounting role defined retain their **original, restricted permissions**, preventing other apps from escalating their privileges.
