
.. highlight:: rest

Matrices
========

This chapter demonstrates some usage of :rst:dir:`req:reqlist` with customized content.

.. req:reqlist:: Tracability
    :sort: reqid


    .. list-table:: {{caption}}
        :widths: 10 60 20 20

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

.. req:reqlist:: Tree Structure
    :sort: reqid


    .. list-table:: {{caption}}
        :widths: 10 60 20 20

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



