# Copyright 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Relation between product templates and move templates now Many2many."""

    # Convert from references in product template
    cr.execute(
        "INSERT INTO account_product_move_product_template_rel"
        " (product_template_id, account_product_move_id)"
        " SELECT pt.id, pt.product_move_id"
        " FROM product_template pt"
        " WHERE NOT pt.product_move_id IS NULL"
    )
