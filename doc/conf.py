
project = 'requirement'
version = '1.0'
author = 'Olivier Heurtier'

#source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []

extensions = ['sphinxcontrib.requirement']

latex_elements = {
'extraclassoptions': 'openany,oneside',
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

req_links = {
    "parents":"children",
    "branches":"leaves",
}
