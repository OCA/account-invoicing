To configure this module, you need to:

#. Install it.

#. A person with accounting manager rights needs to configure the extra product moves
   through menu: Accounting-->Journals-->Extra Product Moves.

#. The extra product moves applicable will be shown on respectively the product
   category or template, but they can not be edited from there, as this is a
   responsibility for people involved in accounting.

Each product move consists of a number of move lines, that will be added to an invoice,
when the invoice is posted. As the lines of a move must be balanced, the same goes for
the lines of the product move.

A product move can be linked to one or more product categories and/or to one or more
product templates. Wether is will be applied for an invoice line, will depend on the
product in the invoice line: is it for the product with this template, or a product in
this category.

The application of an extra product move can be further limited by defining a filter.
If the invoice would be selected by that filter, the extra moves will be included
(for lines with the appropiate template or category). These filters can be defined by
going to the menu: Accounting-->Customers-->Invoices. Then select a filter and store
this under Favorites as a shared filter. Then select the filter defined in this way in
the extra product move.
