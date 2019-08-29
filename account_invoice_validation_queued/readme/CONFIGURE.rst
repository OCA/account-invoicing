#. Jobs are enqueued in the channel ``root.account_invoice_validation_queued``,
   so you must adjust your
   `Odoo configuration <https://github.com/OCA/queue/tree/11.0/queue_job#configuration>`_
   according this.
#. If you want to see queued jobs, you need "Job Queue / Job Queue Manager"
   permission in your user.
#. Configure your invoice/refund sequences as "Standard" instead of "No gap",
   or you'll have concurrent updates problems.
