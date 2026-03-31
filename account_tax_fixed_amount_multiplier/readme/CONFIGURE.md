To configure this module, you need to:

1. Go to *Invoicing > Configuration > Taxes*.
2. Open or create a tax with *Tax Computation* set to **Fixed**.
3. Set the **Amount Multiplier** field to the desired mode:
   - *No Multiplier*: the tax amount is applied once per line.
   - *Quantity (default)*: standard behavior, multiplied by the line
     quantity regardless of the unit of measure.
   - *Product Quantity*: the line quantity is converted to the product's
     unit of measure before multiplying.
   - *Product Weight*: multiplied by the total weight (product quantity ×
     product weight).
