import base64
import io
import zipfile
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ExportInvoiceStatuses(models.TransientModel):
    _name = "export.invoice.statuses"
    _description = "Export Invoice Statuses"

    name = fields.Char("Status")
    code = fields.Char()


class ExportInvoicePdfZip(models.TransientModel):
    _name = "export.invoice.pdf.zip"
    _description = "Export Invoice PDFs as Zip"

    from_date = fields.Date()
    to_date = fields.Date()
    zip_data = fields.Binary("Zip File")

    filter_statuses = fields.Many2many(
        "export.invoice.statuses",
        help="If statuses selected, than only those statuses invoices "
        "are filtered else all status invoices are downloaded.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ExportInvoicePdfZip, self).default_get(fields_list)

        status = {"draft": "Draft", "posted": "Posted", "cancel": "Cancelled"}
        status_codes = list(status.keys())
        statuses = self.env["export.invoice.statuses"].search(
            [("code", "in", status_codes)]
        )
        not_exist_statuses = set(status_codes) - set(statuses.mapped("code"))
        for st in not_exist_statuses:
            self.env["export.invoice.statuses"].create(
                {"name": status.get(st), "code": st}
            )
        return res

    def action_export_pdf_zip(self):
        domain = [
            ("invoice_date", ">=", self.from_date),
            ("invoice_date", "<=", self.to_date),
        ]

        statuses = self.filter_statuses.mapped("code")
        if statuses:
            domain.append(("state", "in", statuses))

        invoices = self.env["account.move"].search(domain)
        report = self.env.ref("account.account_invoices")
        fp = io.BytesIO()
        zf = zipfile.ZipFile(fp, mode="w")
        for invoice in invoices:
            data, format = report._render_qweb_pdf(invoice.id)
            report_name = safe_eval(
                report.print_report_name,
                {"object": invoice, "time": datetime.now().strftime("%Y%m%d%H%S")},
            )
            if invoice.state in ["draft", "cancel"]:
                report_name = "%s/%s_%s" % (report_name, report_name, invoice.id)
            if invoice.date:
                report_name = (
                    report_name[: report_name.rfind("/")]
                    + "/"
                    + invoice.date.strftime("%m")
                    + report_name[report_name.rfind("/") :]
                )
            file_name = "%s.%s" % (report_name, format)
            zf.writestr(file_name, data)

        zf.close()
        self.write({"zip_data": base64.b64encode(fp.getvalue())})
        file_name = "Invoices_" + datetime.now().strftime("%Y%m%d%H%S") + ".zip"

        try:
            form_id = self.env["ir.model.data"].check_object_reference(
                "account_invoice_pdf_export", "view_export_invoice_pdf_zip_form_wizard"
            )[1]
        except ValueError:
            form_id = False
        ctx = self._context.copy()
        return {
            "name": "Export Invoices Zip",
            "type": "ir.actions.act_url",
            "url": "/web/content/?model="
            + self._name
            + "&id="
            + str(self.id)
            + "&field=zip_data&download=true&filename="
            + file_name,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "export.invoice.pdf.zip",
            "views": [(form_id, "form")],
            "view_id": form_id,
            "target": "new",
            "res_id": self.id,
            "context": ctx,
        }
