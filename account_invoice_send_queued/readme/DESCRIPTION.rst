This module allows to enqueue in several jobs the email sending invoices
to be executed in parallel on background, which is normally done serially and
on foreground.

Each invoice creates a job for performing the email sending.
