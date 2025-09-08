import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info("Set specific self-invoice sequence on partners to true by " "default")
    # Before introducting the field allowing us to force the use of a specific
    # sequence for self-invoices, any partner with self-invoicing enabled
    # was using a specific sequence. So we set the field to True by default.
    cr.execute(
        """
        UPDATE res_partner
        SET self_invoice_auto_ref = TRUE
        WHERE self_invoice = TRUE
    """
    )
    # We set also the default value of the field to True
    cr.execute(
        """
        UPDATE
            res_company
        SET
            self_invoice_auto_ref = TRUE
    """
    )
