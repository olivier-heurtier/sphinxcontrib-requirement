
.. highlight:: rest

Example (part 2)
================

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

.. req:req:: This is a second title
    :reqid: REQ-0004

    This is a simple requirement to demonstrate references across multiple documents

See :req:req:`REQ-0002` and :req:req:`REQ-0004`


Table
=====

Full Table
----------

.. list-table:: This is how a normal table looks
    :widths: 20 80
    :header-rows: 1
    :stub-columns: 1
    :width: 100%
    :align: left
    
    * 
      - A
      - B

    *
      - a
      - b

.. req:reqlist:: This is the list of all requirements (no filtering, no sorting)

.. req:reqlist:: This is a *list* produced using **all** options (no filtering, no sorting)
    :fields: reqid, title, priority
    :headers: ID, Title, Priority
    :widths: 20 70 10
    :width: 80%
    :align: right
    :header-rows: 0
    :stub-columns: 2

Filtering and Sorting
---------------------

A list of all requirements with 'second' in the title:

.. req:reqlist::
    :filter: title.find('second')>0

    {%for req in reqs%}{{req['reqid']}}, {%endfor%}


.. req:reqlist:: A custom output with the full content, sorted by reverse ID
    :sort: -reqid


    .. list-table:: {{caption}}
        :widths: 10 70 10 20

        * - ID
          - Description
          - Contract
          - Ref

    {%for req in reqs%}
        * - {{req['reqid']}}
          - {{req['title']}}

            {{req['content']|indent(8)}}

          - {{req['contract']|upper}}
          - :req:ref:`{{req['reqid']}}`
    {%endfor%}


