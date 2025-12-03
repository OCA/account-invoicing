No configuration is required to use this module.

However, for optimal matching:

- Ensure that *OrderReference* in the vendor UBL document corresponds to the 
Purchase Order Ref or the **Vendor Reference** (`partner_ref`).
- Maintain consistent **product names** or **supplier product names** so 
that UBL line descriptions can be matched to the correct purchase order line.

Optional but recommended:
- Define supplier product names (`product.supplierinfo`) to improve matching
accuracy.