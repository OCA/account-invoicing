This module computes, from posted invoices, two average prices and stores them
on product templates and product variants:

- **Average Purchase Price (APP)**, from vendor bills.
- **Average Sale Price (ASP)**, from customer invoices.

Each one is a weighted average: the untaxed subtotal of the invoice lines divided
by the invoiced quantity. Taxes and added costs (landed costs, for instance) are
excluded, and so are refunds, as a returned quantity is not a price the product
was traded at.

Both prices are company dependent: every company gets its own figures, computed
from its own invoices and with its own window settings, so each one sees the
prices it traded at.

Instead of a fixed period, an expanding window is used: the last 30 days are
checked first and, while no invoiced quantity is found, the window is widened 30
days at a time up to 360 days. The first window with data wins, and the range it
covers is stored next to the price, so the figure is always readable in context.
Both the step size and the maximum number of steps are configurable.

Templates and variants are computed independently: a template averages the
invoices of all its variants over a single window, a variant averages only its
own. Because of that, they may end up using different periods.

Values are stored, not computed on the fly. They are refreshed by a daily
scheduled action, and on demand from the product form, where the journal items
behind each price can also be opened.
