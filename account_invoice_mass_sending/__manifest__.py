{
    "name": "Account Invoice Mass Sending",
    "summary": "Mass sending feature for invoices",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA), Open Net Sàrl",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account",
        "queue_job",
    ],
    "data": [
        "data/queue_job.xml",
        "views/account_invoice_views.xml",
        "wizards/account_move_send.xml",  # DESCOMENTADO
    ],
    "installable": True,
    "maintainers": ["jguenat"],
    "development_status": "Beta",
}
