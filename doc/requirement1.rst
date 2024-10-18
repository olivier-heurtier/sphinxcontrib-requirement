
.. highlight:: rest

Example (part 1)
================

Declaration
-----------

.. req:req:: This is a title

    This is a minimal requirement, with no option and an ID auto generated

Req ``REQ-0004`` is referenced there: :req:ref:`REQ-0004`

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

.. req:req:: This is a title
    :reqid: REQ-0002
    :priority: 1
    :contract: c1

    This is a requirement with all possible options defined...

    The description can span multiple lines and includes **ReST** *markups*.

    Even lists are allowed:

    * One
    * Two

See :req:req:`REQ-0004`

.. req:req:: This is a title
    :reqid: REQ-0003
    :priority: 1

    This is a requirement with all possible options defined...

    The description can span multiple lines and includes **ReST** *markups*.


See :req:req:`REQ-0004`

See :req:req:`REQ-0002`

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

CSV
---

Requirements Imported for c1:

.. req:req::
    :csv-file: test1.csv
    :filter: contract=='c1'

Requirements Imported for c3:

.. req:req::
    :csv-file: test1.csv
    :filter: contract=='c3'
