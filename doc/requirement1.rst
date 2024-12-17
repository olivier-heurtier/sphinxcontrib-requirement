
.. highlight:: rest

Chapter 1
=========

.. req:req:: This is req 01-01
    :reqid: REQ-0101

    First requirements for local links (links in the same rst file)

Forward link to :req:req:`REQ-0103`.

.. req:req:: This is req 01-02
    :reqid: REQ-0102

    Second requirements for links in another rst file

Link in another rst file :req:req:`REQ-0202`

.. req:req:: This is req 01-03
    :reqid: REQ-0103

    Third requirements for local links (links in the same rst file)

Backward link to :req:req:`REQ-0101`.

Examples
========

Declaration
-----------

.. req:req:: This is a title
    :reqid: REQ-0001
    :parents: REQ-0004, CSV-002

    This is a minimal requirement, with no option

Req ``REQ-0004`` is referenced there: :req:ref:`REQ-0004`

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

.. req:req:: This is a title
    :reqid: REQ-0002
    :priority: 1
    :contract: c1
    :parents: CSV-002

    This is a requirement with a lot of options defined...

    The description can span multiple lines and includes **ReST** *markups*.

    Even lists are allowed:

    * One
    * Two

See :req:req:`REQ-0004`

.. req:req:: This is a title
    :reqid: REQ-0003
    :priority: 1

    This is a requirement with again a lot of options and with a comment

    |

    The comment can span multiple lines and includes **ReST** *markups*.


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
