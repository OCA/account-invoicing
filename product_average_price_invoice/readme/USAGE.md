## Consulting the prices

Go to a product template or a product variant, *General Information* tab, right
below the *Cost* field see **APP** and **ASP**, each one followed by the period 
it was computed for (*From ... to ...*)

A price of `0.00` labelled *No data* means no invoiced quantity was found within
the widest window. In that case no period is stored, and the arrow button opens
an empty list.

What is shown always belongs to the active company. Switching companies shows
the prices that company computed from its own invoices.

## Refreshing automatically

The *Update product average prices* scheduled action runs every night and
recomputes, for every company, the products it invoiced within the widest
window, at both variant and template level. Its frequency can be changed in
*Settings > Technical > Scheduled Actions*.

## Configuring the window

Go to *Settings > Accounting*, section *Product Average Prices*. Both values
belong to the active company:

- **Step size (days)**: length of each step of the window, 30 by default.
- **Max steps**: how many times the window may be widened before giving up, 12
  by default, so the search goes back 360 days at most.

Changing them does not recompute anything by itself. Stored prices keep the
window they were computed with until the scheduled action or a button refreshes
them.
