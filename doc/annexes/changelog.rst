
Change Log
==========

**Version 1.4.0**

- Add a new ``serial`` variable, with a number unique in the whole set of ReST documents, that
  can be used in ``req_idpattern``. Previous serial variable is renamed to ``doc_serial``.
- Fix rendering of empty list of requirements
- Regexp can be used in filters

**Version 1.3.0** (14/01/2025)

- Add Jinja blocks in :file:`req.rst.jinja2` to allow reuse
- Option to customize the text used in the :rst:role:`req:req` role.
  Defaut is to use the ``reqid``.
- Fix bad line height in table introduced by \sphinxAtStartPar on empty link value
- Add a ``label`` option to the :rst:dir:`req:req` directive. It can be used in replacement of reqid
  to define links and references. It is useful when IDs are generated by this extension.

**Version 1.2.0** (10/01/2025)

- Support more standard way of customization HTML CSS and PDF
  (latex_element preamble, etc.) so that styles can be added.
  No need normally to redefine the files :file:`req.css` or :file:`req.preamble`.
- Support very long titles
- Move part of the layout from HTML/LaTeX templates to rst templates,
  using containers and roles for the styling.
- Add pseudo attribute `text_content` and `text_title` to the requirements.
  They are preprocessed text where substitutions are done and can be used
  rst templates or CSV exports.
- Fix: properly escape characters in HTML & LaTeX
- Ability to export a list of requirement to a CSV
- Provide default value to all options to be used in filtering
- Add option `hidden` to :rst:dir:`req:reqlist`

**Version 1.1.0** (06/01/2025)

- Add option `hidden` to :rst:dir:`req:req`
- Fix uniqueness of generated ID
- Give more example of customization, using the container directive

**Version 1.0.0** (17/12/2024)

First initial version.
