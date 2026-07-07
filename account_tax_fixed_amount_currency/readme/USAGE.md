Once configured, the tax behaves like a standard fixed tax but with automatic
currency conversion. When creating an invoice in a foreign currency, the tax
amount will be converted from the tax's currency to the document's currency.

For example, if a tax is configured with a fixed amount of CHF 10 and the
invoice is in EUR, the tax amount will be converted from CHF to EUR using
the exchange rate at the invoice date.

If `account_tax_fixed_amount_multiplier` is also installed, configure the
multiplier on the tax as usual. The multiplier is applied before conversion,
so a tax defined in CHF per product unit or kilogram is first multiplied by
the relevant quantity, then converted to the invoice currency.
