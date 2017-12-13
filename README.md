[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Build Status](https://travis-ci.org/muk-it/muk_dms.svg?branch=master)](https://travis-ci.org/muk-it/muk_dms)
[![codecov](https://codecov.io/gh/muk-it/muk_dms/branch/10.0/graph/badge.svg)](https://codecov.io/gh/muk-it/muk_dms)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0c64c4c207b8466b9ed57aa7d0631cb6)](https://www.codacy.com/app/keshrath/pdfconv?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=keshrath/pdfconv&amp;utm_campaign=Badge_Grade)

# MuK Document Management System

MuK Documents is a module to create, manage and view files within Odoo.

---

<img align="center" src="https://github.com/muk-it/muk_dms/blob/9.0/muk_dms/static/description/demo.gif"/>

## Place Documents into other models

### Model

```python
file = fields.Many2one('muk_dms.file', string='Document')
```

### Record (XML)

```xml
<field name="dmsfile" widget="dms_file" string="Datei" />
```

```xml
<field name="dmsfile" widget="dms_file" string="Datei" filename="field_filename" directory="ref_directory_id" />
```

```xml
<field name="dmsfile" widget="dms_file" string="Datei" downloadonly="downloadonly" />
```

## Requirements

* mammoth

```bash
$ sudo pip install mammoth
```
