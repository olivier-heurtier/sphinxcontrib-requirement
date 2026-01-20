
.. highlight:: rest

Examples (part 2)
=================

Basic Examples
--------------

Here you will find some basic requirements demonstrating references, backward or forward into the list of rst files.

.. req:req:: This is req 02-01
    :reqid: REQ-0201

    First requirements for local links (links in the same rst file)

Forward link to :req:req:`REQ-0203`.

.. req:req:: This is req 02-02
    :reqid: REQ-0202

    Second requirements for links in another rst file

Link in another rst file :req:req:`REQ-0102`

.. req:req:: This is req 02-03
    :reqid: REQ-0203

    Third requirements for local links (links in the same rst file)

Backward link to :req:req:`REQ-0201`.

.. req:req:: This is yet another example
    :reqid: REQ-0004

    This is a simple requirement to demonstrate references across multiple documents

See :req:req:`REQ-0002` and :req:req:`REQ-0004`

Req ``REQ-0002`` is referenced there: :req:ref:`REQ-0002`

Generating ID
-------------

.. req:req:: Generation 3
    :label: GEN3
    :children: GEN1

    This is a third test of ID generation

This requirement is referenced there: :req:ref:`GEN3`

See also :req:req:`GEN1`
 
Table
=====

This chapter demonstrates the :rst:dir:`req:reqlist` directive.

This is a normal table:

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

This is the list of all requirements defined in this document.

.. code-block:: rst

    .. req:reqlist:: This is the list of all requirements (no filtering, no sorting)

renders as:

.. req:reqlist:: This is the list of all requirements (no filtering, no sorting)

This is still the list of all the requirements but with a customized list of columns.

.. code-block:: rst

    .. req:reqlist:: This is a *list* produced using **all** options (no filtering, no sorting)
        :fields: reqid, title, priority, _parents
        :headers: ID, Title, Priority, Parents
        :widths: 20 40 20 30
        :width: 80%
        :align: right
        :header-rows: 0
        :stub-columns: 2

renders as:

.. req:reqlist:: This is a *list* produced using **all** options (no filtering, no sorting)
    :fields: reqid, title, priority, _parents
    :headers: ID, Title, Priority, Parents
    :widths: 20 40 20 30
    :width: 80%
    :align: right
    :header-rows: 0
    :stub-columns: 2

The same directive can be used to produce a plain list, with no table.

.. code-block:: rst

    .. req:reqlist::
        :filter: title.find('Generation')>=0

        {{reqs|join(', ', attribute='reqid')}}

renders as:

.. req:reqlist::
    :filter: title.find('Generation')>=0

    {{reqs|join(', ', attribute='reqid')}}

Another example illustrating usage of an attribute not defined on all requirements and
listing all priority 1 requirements:

.. code-block:: rst

    .. req:reqlist::
        :filter: priority==1

        {{reqs|join(', ', attribute='reqid')}}

renders as:

.. req:reqlist::
    :filter: priority==1

    {{reqs|join(', ', attribute='reqid')}}

.. only:: html

    The same list can be hidden and exported to a `CSV file <prio1.csv>`_ with:

    .. code-block:: rst

        .. req:reqlist::
            :filter: priority==1
            :hidden:
            :csv-file: prio1.csv

.. raw:: latex

    The same list can be hidden and exported to a
    \textattachfile[]{prio1.csv}{CSV file} with:

.. only:: latex

    .. code-block:: rst

        .. req:reqlist::
            :filter: priority==1
            :hidden:
            :csv-file: prio1.csv

.. req:reqlist::
    :filter: priority==1
    :hidden:
    :csv-file: prio1.csv

If the list is empty, a defaut message is displayed.

.. code-block:: rst

    .. req:reqlist::
        :filter: priority==5

renders as:

    .. req:reqlist::
        :filter: priority==5

This directive accepts a content to better customize the rendering.

.. code-block:: rst

    .. req:reqlist:: A custom output with the full content, sorted by reverse ID
        :sort: -reqid


        .. list-table:: {{caption}}
            :widths: 20 50 20 20
            :class: longtable

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

renders as:

.. req:reqlist:: A custom output with the full content, sorted by reverse ID
    :sort: -reqid


    .. list-table:: {{caption}}
        :widths: 20 50 20 20
        :class: longtable

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

.. warning::

    Do not forget to *indent* as needed values that can span multiple lines.

Filters can use some Python functions. For example ``re`` module is available.

.. code-block:: rst

    .. req:reqlist:: Using advanced filtering with regexp
        :filter: re.search(r'\svery very\s', content) and priority==1

renders as:

.. req:reqlist:: Using advanced filtering with regexp
    :filter: re.search(r'\svery very\s', content) and priority==1
