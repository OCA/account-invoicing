* Allow to enqueue for validating invoices of different date.
* There's a chance that if you perform several enqueues of invoice validations
  from different dates, the order of the validated invoices, and thus, the
  number given for it, will result disordered.
