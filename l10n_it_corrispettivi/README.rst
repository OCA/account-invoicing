.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

====================================
Italian Localization - Corrispettivi
====================================

Questo modulo permette di generare le ricevute specificando le varie aliquote per riga
(le righe della ricevuta hanno gli stessi automatismi di quelle della fattura) e quindi registrare le ricevute una per una.
Un esempio tipico di questo caso d’uso è la vendita tramite sito di e-commerce.

Chi invece emette scontrini (e non ha un POS integrato con Odoo) dovrà registrare in contabilità, a fine giornata, gli incassi totali.

Configuration
=============

Creare almeno un sezionale di tipo vendita su cui saranno registrati i corrispettivi,
deve avere il flag corrispettivi abilitato.

Se necessario, creare una posizione fiscale per i corrispettivi, deve avere il flag corrispettivi abilitato.
Questa posizione fiscale verrà assegnata a tutti i nuovi partner aventi il flag *Usa corrispettivi* abilitato.

Utilizzando un utente del gruppo Contabilità & Finanza > Contabilità, sul partner associato al public user:

* Modificare, se necessario, i conti di debito e di credito da utilizzare per i corrispettivi;
* Abilitare il flag *Usa corrispettivi*

Nota: di default, il public user è disabilitato (flag active disabilitato).

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/122/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-italy/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Simone Rubino <simone.rubino@agilebg.com>

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
