# coding: utf-8
def post_init_hook(cr, pool):
    cr.execute(
        """ UPDATE account_invoice_line
        SET discount_real = discount
        WHERE invoice_id IN (
            SELECT id FROM account_invoice
            WHERE move_id IS NOT NULL)
        """)
