
.. list-table:: {{caption}}
    :align: {{align}}
    :width: {{width}}
    :widths: {{widths}}
    :header-rows: {{header_rows}}
    :stub-columns: {{stub_columns}}

    * 
{%for H in headers%}
      - {{H}}
{%endfor%}

{%for req in reqs%}
    *
{%for f in fields%}
      - {{req[f]}}
{%endfor%}

{%endfor%}
