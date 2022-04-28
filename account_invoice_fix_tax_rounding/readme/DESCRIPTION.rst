When using global rounding, some inconsistencies might appear in the final tax amount,
due to floating point representation quicks (see discussion on python Decimal class).

This happens only very rarely, here's an example:

if total VAT is something like 100.005, and precision is 2, it gets rounded to 100.01;
but sometimes in Python you get something like this:

>>> 99.705 + .1 + .1 + .1
100.00499999999998

Now, with precision 2, 100.00499999999999 gets rounded to 100.00.

On the other hand:
>>> 99.805 + .1 + .1
100.005

and that would be rounded to 100.01.

Method compute_all() in account.tax and _recompute_dynamic_lines() in account.move
do use higher precision to compute amounts, but they don't round them at that precision.

We mitigate the problem by rounding amounts at higher precision (+5 digits). This turns e.g.
100.00499999999999 into 100.0050000.

Notice that this bug bites only when there's a 5 in the precision + 1 position in the amount
and, at the same time, floating point representation turns it into 49999999. In all other
cases, using higher precision alone like account.tax and account.move do is enough to yield
the correct result with global rouding.
