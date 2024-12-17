
project = 'requirement'
version = '1.0'

#source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []

extensions = ['sphinxcontrib.requirement.req']

latex_elements = {
  'papersize': 'a4paper',
  'pointsize': '10pt',
  'preamble': u'''

\\usepackage{bbding,pifont} %% two dingbat fonts
\\DeclareUnicodeCharacter{2750}{\\ding{238} }

\\definecolor{xxxreqbg}{rgb}{0.85,0.85,0.85}
\\definecolor{xxxreqidbg}{rgb}{0.95,0.95,0.95}

\\usepackage[framemethod=TikZ]{mdframed}
\\newmdenv[backgroundcolor=xxxreqbg]{xxxreq}
\\newmdenv[roundcorner=5pt,leftmargin=20,rightmargin=10,backgroundcolor=xxxreqidbg]{sphinxclassxxxreqid}

'''
}

# https://tex.stackexchange.com/questions/666826/why-is-my-environment-not-taking-the-style-i-specify
# https://en.wikibooks.org/wiki/LaTeX/Footnotes_and_Margin_Notes
