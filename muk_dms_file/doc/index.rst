==================
MuK Documents File
==================

MuK Documents is a module to create, manage and view files directly within Odoo.
MuK Documents File enables a new save option. Files saved with this option will be
stored inside a file storage. The file store is not synronized on both sides. So
the saved files should not be changed manually, as this can lead to unexpected
system states.

Installation
============

To install this module, you need to:

Download the module and add it to your Odoo addons folder. Afterward, log on to
your Odoo server and go to the Apps menu. Trigger the debug modus and update the
list by clicking on the "Update Apps List" link. Now install the module by
clicking on the install button.

Configuration
=============

No additional configuration is needed to use this module.

Usage
=============

I case you want to change the save type of an existing Root Setting be aware that this
can trigger a heavy migration process, depending on how many files are currently stored.

Before you start the migration process make sure the following conditions are met:

* no one else is using the system at the time of migration
* no files are locked either by the system or users
* Odoo has writing rights to the given directory path

Credits
=======

Contributors
------------

* Mathias Markl <mathias.markl@mukit.at>

Author & Maintainer
-------------------

This module is maintained by the `MuK IT GmbH <https://www.mukit.at/>`_.

MuK IT is an Austrian company specialized in customizing and extending Odoo.
We develop custom solutions for your individual needs to help you focus on
your strength and expertise to grow your business.

If you want to get in touch please contact us via mail
(sale@mukit.at) or visit our website (https://mukit.at).
