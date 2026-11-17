def post_init_hook(env):
    lines = env["account.move.line"].search(
        [("display_type", "=", "product"), ("product_id", "!=", False)]
    )
    hidden_lines = env["account.move.line"]
    for line in lines:
        product_name = line.product_id.with_context(
            lang=line.move_id._get_lang()
        ).display_name
        if line.name and product_name and product_name not in line.name:
            hidden_lines |= line
    if hidden_lines:
        env.cr.execute(
            """
                UPDATE account_move_line
                SET hide_product_name = TRUE
                WHERE id = ANY(%s)
            """,
            (hidden_lines.ids,),
        )
