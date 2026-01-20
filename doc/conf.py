
project = 'requirement'
version = '1.0'
author = 'Olivier Heurtier'

master_doc = 'index'
exclude_patterns = []

extensions = ['sphinxcontrib.requirement']

# test if substitution are correctly applied everywhere (title, content, export in CSV)
# style the comment
rst_prolog = """

.. |product| replace:: sphinxcontrib-requirement

.. raw:: html

    <style>

        .comment {
            margin-left: 30px;
            margin-right: 20px;
            margin-bottom: 10px;
            padding: 5px;
            background-color: #F4F4F4;
            border-style: solid;
            border-radius: 5px;
            border-width: 1px;
            border-color: black;
        }
    </style>

"""

latex_elements = {
'extraclassoptions': 'openany,oneside',
'preamble':r'''
\usepackage{attachfile2}
\usepackage[framemethod=TikZ]{mdframed}

% custo styling of the comment
\definecolor{commentbg}{rgb}{0.9,0.9,0.9}
\newmdenv[roundcorner=5pt,leftmargin=5,rightmargin=10,backgroundcolor=commentbg]{sphinxclasscomment}

''',
'atendofbody': r'''
  \listoftables
  \listoffigures
 '''
}

req_options = dict(
    contract="lambda argument: directives.choice(argument, ('c1', 'c3'))",
    priority="directives.positive_int",
)

from docutils.parsers.rst import directives
from sphinxcontrib.requirement import req
def yesno(argument):
    return directives.choice(argument, ('yes', 'no'))
# be aware that docutils/sphinx is lowering the case
req.ReqDirective.option_spec['answer'] = yesno

req_links = {
    "parents":"children",
    "branches":"leaves",
}

req_idpattern = 'GEN-{serial:02d}-{doc}{doc_serial:03d}'
req_reference_pattern = '{reqid}-{text_title}'
