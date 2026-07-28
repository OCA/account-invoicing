Provides a new visible sequence field on invoice lines which helps users to
identify invoice lines in the UI and printed reports.

The sequence number always starts at 1 and rises incrementally: 1, 2, 3,
... To keep it that way, all sequence numbers are recalculated when invoice
lines are created or reordered. Section and note lines are skipped. The line
number is printed on the invoice report.
