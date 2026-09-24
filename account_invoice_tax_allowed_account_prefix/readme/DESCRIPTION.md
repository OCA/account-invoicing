This module allows restricting the usage of taxes on invoice lines based on the account
code prefix.

A new field **Allowed Account Prefixes** is added on taxes. When set, the tax can only be
applied on invoice lines whose account code starts with one of the configured prefixes.

This is useful in accounting contexts where multiple taxes share the same rate but must
be selected depending on the nature of the expense (e.g. goods, services, investments).
