This module allows to enqueue in several jobs the account validation process
to be executed in paralell on background, which is normally done serially and
on foreground.

Each invoice creates a job for performing the validation, but you will only be
able to enqueue invoices for the same date.
