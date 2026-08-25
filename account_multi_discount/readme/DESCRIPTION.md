This module replaces the single ``discount`` percentage on invoice lines
(``account.move.line``) with an unlimited list of percentage discounts that
compose **multiplicatively**.

A new JSON field ``discount_distribution`` stores the ordered list of
percentages and a dedicated OWL widget exposes it as colored tags with a
popup editor, much in the same fashion as the analytic distribution widget.

The legacy ``discount`` field is preserved as a stored, computed aggregate so
that the existing tax engine, reports and third-party modules keep working
without modification.
