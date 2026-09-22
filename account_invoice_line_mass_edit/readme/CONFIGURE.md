By default, the mass edit action available on the invoice lines list is
configured with the *Analytic Distribution* field only.

Two technical fields, *Company* and *Analytic Precision*, are also configured
because the analytic distribution widget requires them, but they are hidden in
the mass editing wizard.

To add more fields that can be updated in mass:

1.  Go to *Settings > Technical > Actions > Server Actions*.
2.  Open the *Mass Edit Invoice Lines* action.
3.  In the *Fields* tab, add the fields you want (the fields must belong to
    the *Journal Item* model).
