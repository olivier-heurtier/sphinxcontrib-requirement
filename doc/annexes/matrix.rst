
.. highlight:: rest

Matrices
========

This chapter demonstrates some usage of :rst:dir:`req:reqlist` with customized content.

.. req:reqlist:: Tracability
    :sort: reqid
    :fields: reqid, title, parents, children


    .. list-table:: {{caption}}
        :widths: 20 50 20 20

        * - ID
          - Title
          - Parents
          - Children

    {%for req in reqs%}
        * - {{req['reqid']}}
          - {{req['title']}}
          - {{req['_parents']}}
          - {{req['_children']}}
    {%endfor%}

.. req:reqlist::
    :hidden:
    :sort: reqid
    :fields: reqid, text_title, text_content, parents, children
    :csv-file: tracability.csv


.. req:reqlist:: Tree Structure
    :sort: reqid


    .. list-table:: {{caption}}
        :widths: 20 50 20 20

        * - ID
          - Title
          - Branches
          - Leaves

    {%for req in reqs%}
        * - {{req['reqid']}}
          - {{req['title']}}
          - {{req['_branches']}}
          - {{req['_leaves']}}
    {%endfor%}


.. only:: html

    All priority 2 requirements are in `CSV file <prio2.csv>`_

.. raw:: latex

    All priority 2 requirements are in 
    \textattachfile[]{annexes/prio2.csv}{CSV file}

.. req:reqlist::
    :filter: priority==2
    :hidden:
    :csv-file: prio2.csv
    :fields: reqid, text_title, text_content, priority, contract
    :headers: ID, Title, Content, Priority number, Contract number

