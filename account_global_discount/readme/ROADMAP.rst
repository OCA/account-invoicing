* Not all the taxes combination can be compatible with global discounts, as
  the generated journal items won't be correct for taxes declarations. An error
  is raised in that cases.
* Currently, taxes in invoice lines are mandatory with global discounts.
* No tax tags are populated for the global discount move lines, only `tax_ids`.
