Define Invoice Lines for complimentary Products.

Invoice Lines set as `Complimentary` will be charged on a configured account instead of the invoice's account.

For example: You are invoicing coffee to a customer and you want to give them napkins for free.

The Invoice Lines are:

+-----------------+-------------+-----------+---------------+-----+
| Account         |    Name     |     Price | Complimentary | Tax |
+=================+=============+===========+===============+=====+
| Receivable      | Coffee      |    100.00 |               | 22% |
+-----------------+-------------+-----------+---------------+-----+
| Product Sales   | Napkins     |     10.00 |          True | 22% |
+-----------------+-------------+-----------+---------------+-----+


Invoice total is:

(100 + 100 * 22%) + (10 + 10 * 22%) = 122 + 12.2 = 134.2.

When confirmed, the created Journal Items are:

+-----------------+-------------+-----------+-----------+
| Account         |    Name     |     Debit |    Credit |
+=================+=============+===========+===========+
| Receivable      |             |    122.00 |           |
+-----------------+-------------+-----------+-----------+
| Tax Received    |             |           |     24.20 |
+-----------------+-------------+-----------+-----------+
| Complimentary   | Napkins     |     12.20 |           |
+-----------------+-------------+-----------+-----------+
| Product Sales   | Napkins     |           |     10.00 |
+-----------------+-------------+-----------+-----------+
| Product Sales   | Coffee      |           |    100.00 |
+-----------------+-------------+-----------+-----------+

The Journal Entry Total is still 134.20 but the Invoice's Amount Due becomes 122:
the Napkin and its Tax won't be paid by the customer.
