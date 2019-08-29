This module allows to enqueue in several jobs the sales orders invoicing
process to be executed in paralell on background, which is normally done
serially and on foreground.

Jobs are split following the same criteria as standard Odoo: grouping by
order invoicing address and order currency.
