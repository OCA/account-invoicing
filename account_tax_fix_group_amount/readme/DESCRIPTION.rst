This module creates a new type of tax to fix the following unexpected behavior.

Create a `Percentage of Price` tax having 22 percent amount.

Create a `Group of Taxes` tax having:

- 8,8 `Percentage of Price` tax
- 13,2 `Percentage of Price` tax

Anyone would expect that the amounts computed by both taxes are always the same.
This might not be the case, because of rounding issues.

This module then introduces a new type of tax called `Last percentage of group`.
Defining the group tax with:

- 8,8 `Percentage of Price` tax
- 13,2 `Last percentage of group` tax

You can be sure that this tax will have the the same amount as the `Percentage of Price` tax having 22 percent amount.
