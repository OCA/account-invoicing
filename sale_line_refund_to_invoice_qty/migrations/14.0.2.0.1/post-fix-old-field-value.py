import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sol_model = env["sale.order.line"]
    field_definition = env["ir.model.fields"].search(
        [("name", "=", "sale_qty_to_reinvoice"), ("model", "=", "account.move.line")],
        limit=1,
    )
    if field_definition:
        reference_date = field_definition.create_date or field_definition.write_date
        env.cr.execute(
            """
        update account_move_line set sale_qty_to_reinvoice = True
        where create_date <= %s and
        (sale_qty_to_reinvoice = False or sale_qty_to_reinvoice is null)
        """,
            (reference_date,),
        )
        env.cr.commit()
        query = """
        with invoice_lines as (
        select rel.order_line_id, sum(coalesce(aml.quantity, 0)) as quantity
        from account_move_line as aml
        inner join account_move as am on am.id = aml.move_id
        inner join sale_order_line_invoice_rel as rel on rel.invoice_line_id  = aml.id
        where am.state = 'posted' and am.move_type = 'out_invoice'
        group by rel.order_line_id
        ), credit_lines as (
            select rel.order_line_id, sum(coalesce(aml.quantity, 0)) as quantity
            from account_move_line as aml
            inner join account_move as am on am.id = aml.move_id
            inner join sale_order_line_invoice_rel as rel on rel.invoice_line_id  = aml.id
            where am.state = 'posted' and am.move_type = 'out_refund'
            and aml.sale_qty_to_reinvoice = true
            group by rel.order_line_id
        )
        select
            sol.id
        from sale_order_line as sol
        inner join sale_order as so on so.id = sol.order_id and so.state in ('sale', 'done')
        left join invoice_lines as il on sol.id = il.order_line_id
        left join credit_lines as cl on sol.id = cl.order_line_id
        where (coalesce(il.quantity, 0) - coalesce(cl.quantity, 0)) != sol.qty_invoiced
        and (sol.create_date >= %s or sol.write_date >= %s)

        """
        env.cr.execute(query, (reference_date, reference_date))
        lines_with_problems = [data[0] for data in env.cr.fetchall()]
        if lines_with_problems:
            sol_lines = sol_model.search(
                [
                    ("id", "in", lines_with_problems),
                    ("product_id.type", "!=", "service"),
                ]
            )
            _logger.debug("total lines to reprocess: %s", str(len(sol_lines)))
            sol_lines._get_invoice_qty()
