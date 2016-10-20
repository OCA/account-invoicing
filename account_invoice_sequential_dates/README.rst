.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Check invoice date consistency
==============================

This module prohibits the validation of an invoice if there's a date
inconsistency.

The check is made against date and sequence number.

Users won't be able to procede with the validation if a confirmed invoice with
greater date already exists.

Usage
=====

When an user validate an invoice, Odoo reads data and number and checks if exist an invoice with bigger data, yet

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/122/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* `Odoo Italia Network <http://www.odoo-italia.net/>`_
* Davide Corio <davide.corio@abstract.it>
* Luca Subiaco <subluca@gmail.com>
* Simone Orsi <simone.orsi@domsense.com>
* Mario Riva <mario.riva@domsense.com>
* Mauro Soligo <mauro.soligo@katodo.com>
* Giovanni Barzan <giovanni.barzan@gmail.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Roberto Onnis <onnis.roberto@gmail.com>
* Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
* Alex Comba <alex.comba@agilebg.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.