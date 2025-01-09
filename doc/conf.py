
project = 'requirement'
version = '1.0'
author = 'Olivier Heurtier'

master_doc = 'index'
exclude_patterns = []

extensions = ['sphinxcontrib.requirement']

latex_elements = {
'extraclassoptions': 'openany,oneside',
'preamble':r'\usepackage{attachfile}',
'atendofbody': r'''
  \listoftables
  \listoffigures
 '''
}

# https://tex.stackexchange.com/questions/666826/why-is-my-environment-not-taking-the-style-i-specify
# https://en.wikibooks.org/wiki/LaTeX/Footnotes_and_Margin_Notes

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

req_idpattern = 'GEN-{doc}{serial:03d}'

# test if substitution are correctly applied everywhere (title, content, export in CSV)
rst_prolog = """

.. |product| replace:: sphinxcontrib-requirement


"""
