
.. highlight:: rest

Matrices
========

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
          - {{req['parents']|links}}
          - :req:req:`children::{{req['reqid']}}`
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
          - {{req['branches']|links}}
          - :req:req:`leaves::{{req['reqid']}}`
    {%endfor%}



