To edit the invoice's due date, we have several scenarios:

* A Payment Term is set. In this case, no extra field will be shown while in
  draft, as the standard flow allows us to edit the Payment Term directly, or
  delete it and set a due date manually.
  Once the invoice is posted, a new field will be shown in the view above the
  Payment Term, allowing the due date to be changed.
* No Payment Term is set, and the due date is set manually. In this case, the
  due date is editable while in draft, as with the standard Odoo flow. However,
  once posted, the field will remain editable.

(All the above are considering the user belongs to the security group refered in
"Configuration")
