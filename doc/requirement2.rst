
.. highlight:: rest

Requirement Extension
=====================

Req 0001 is referenced there: :req:ref:`0001`

.. req:req:: This is a second title
    :id: 0002

    This is a simple requirement

See :req:req:`0001` and :req:req:`0002`


Table
=====

.. list-table:: Table Témoin
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


.. req:reqlist:: This is a *list* with all options set
    :fields: reqid, title, priority
    :headers: ID, Title, Priority
    :widths: 20 70 10
    :width: 80%
    :align: right
    :header-rows: 0
    :stub-columns: 2

.. req:reqlist:: This is **another** *list* with no options

.. req:reqlist:: A custom list with a filter
    :filter: title.find('second')>0

    {%for req in reqs%}{{req['reqid']}}, {%endfor%}


.. req:reqlist:: A custom output with the full content
    :sort: -reqid


    .. list-table:: {{caption}}
        :widths: 10 70 20

        * - ID
          - Description
          - Ref

    {%for req in reqs%}
        * - {{req['reqid']}}
          - {{req['title']}}

            {{req['content']|indent(8)}}

          - :req:ref:`{{req['reqid']}}`
    {%endfor%}


