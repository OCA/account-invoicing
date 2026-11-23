In the Invoicing settings, under *Invoicing Mode*:

- *Invoicing day* is the day of the month the monthly invoicing is
  executed. A day the month does not have (31 by default) means its last
  day.
- *Date invoices on the previous month* dates the invoices on the last day
  of the month preceding the execution, instead of the day of the
  execution.

The invoicing is executed by a nightly scheduled action, so with the
default settings what is delivered on the last day of the month, after
the action has run, is only invoiced one month later. To invoice a whole
month at once, set the invoicing day to 1 and enable *Date invoices on
the previous month*: the invoicing executed on the 1st then covers
everything delivered until the last day of the previous month, and is
dated on that day.

The previous month has to be open for invoicing when the invoicing is
executed: with a lock date already set on it, the invoices cannot be
posted on that date.
