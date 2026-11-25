# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Remove the links that are not set anymore by the module: lines that are not
    product, section, subsection or note lines (taxes, payment terms...) and lines
    of moves that are not reversals (e.g. the draft invoice created by the
    "Reverse and Create Invoice" option of the reversal wizard).
    """
    cr.execute(
        """
        UPDATE account_move_line aml
        SET origin_line_id = NULL
        FROM account_move am
        WHERE am.id = aml.move_id
            AND aml.origin_line_id IS NOT NULL
            AND (
                am.reversed_entry_id IS NULL
                OR aml.display_type NOT IN (
                    'product', 'line_section', 'line_subsection', 'line_note'
                )
            )
        """
    )
