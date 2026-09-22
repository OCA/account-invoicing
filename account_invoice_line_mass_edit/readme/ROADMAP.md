The invoice lines are mass updated from a read-only list view (opened with a
smart button on the invoice) where the *Mass Edit* button opens the wizard of
the *server_action_mass_edit* module. This solution was preferred to a mass
editable list (editable list view, or the native `multi_edit="1"` feature of
Odoo 18) for the following reasons:

- Some fields must be written at the same time. For instance the start and end
  dates of a period (fields added on the invoice lines by modules such as
  *account_invoice_start_end_dates*) can't be edited separatly (constraint)

- It gives a fine control on what can be updated in mass: the fields proposed by
  the wizard are configured on the *Mass Edit Invoice Lines* server action, so
  that only the fields that make sense for a mass update are exposed (see the
  *Configuration* section), instead of every field of the journal items.

- Only the selected lines are updated, and the sections and notes displayed in
  the list are explicitly excluded from the update.

The *Analytic Distribution* field is configured by default on the action. Because of
its widget, it does not work out of the box and this modules aims make it editable via
the mass edit button.
