
.. highlight:: rest

Examples (part 1)
=================

Basic Examples
--------------

Here you will find some basic requirements demonstrating references, backward or forward into the list of rst files.

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

.. req:req:: This is a requirement with a very strange ID: ID<23&4,>
    :reqid: ID<23&4,>

    This is a requirement with a very strange ID: ID<23&4,>

.. req:req:: This is a requirement of |product| with a substitution

    This is a requirement of |product| with a substitution

.. req:req:: This is a requirement with a very very very very very very very very very very very very very very very very very very very very very very very very very very very long title
    :priority: 1

    This is a requirement with a very very very long title

Customization Examples
----------------------

The requirements in this chapter illustrate how to use the customized options and links.

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
    :answer: yes
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
    :children: REQ-0004
    :sort: reqid
    :filter: contract=='c1'

    This is a requirement with usage of the reversed link (children) and with a comment

    |

    The comment can span multiple lines and includes **ReST** *markups*.


See :req:req:`REQ-0004`

See :req:req:`REQ-0002`

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

Importing from a CSV
--------------------

Requirements can be imported from an external CSV file.

First we import only the requirements for c1:

.. req:req::
    :csv-file: test1.csv
    :sort: reqid
    :filter: contract=='c1'

And then the requirements for c3 (hidden).

.. req:req::
    :csv-file: test1.csv
    :filter: contract=='c3'
    :hidden:

Generating ID
-------------

.. req:req:: Generation 1
    :label: GEN1
    :children: GEN2

    This is a first test of ID generation

This requirement is referenced there: :req:ref:`GEN1`

.. req:req::
    :label: GEN2
    :children: GEN2

    An additional test for ID generation with no title

See also :req:req:`GEN2`
 