
# https://www.sphinx-doc.org/en/master/development/tutorials/adding_domain.html

import os
from typing import TYPE_CHECKING, Any, ClassVar, cast

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from sphinx.util import texescape
from sphinx.util.docutils import SphinxDirective
from sphinx.util.template import ReSTRenderer
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.errors import NoUri

if True:
    from collections.abc import Set

    from docutils.nodes import Element, Node

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import ExtensionMetadata, OptionSpec
    from sphinx.writers.html5 import HTML5Translator
    from sphinx.writers.latex import LaTeXTranslator

PREFIX = 'REQ'
FORMAT = '%(prefix)s-%(docid)s-%(reqid)s'
DOCID = ''

#______________________________________________________________________________
class xxxreq_node(nodes.Element):
    pass

def visit_xxxreq_node(self: HTML5Translator, node: xxxreq_node) -> None:
    return
    self.body.append(self.starttag(node, 'div', CLASS='xxxreq'))
    self.body.append('<p style="margin-left:-4em; margin-bottom: -2.3em">'+node['reqid']+'</p>\n')

def depart_xxxreq_node(self: HTML5Translator, node: xxxreq_node) -> None:
    return
    self.body.append('</div>\n')

def latex_visit_xxxreq_node(self: LaTeXTranslator, node: xxxreq_node) -> None:
    return
    self.body.append('\n\\begin{xxxreq}{')
    self.body.append(self.hypertarget_to(node))


def latex_depart_xxxreq_node(self: LaTeXTranslator, node: xxxreq_node) -> None:
    return
    self.body.append('\n}\n\\end{xxxreq}\n')


class XXXReq(SphinxDirective):
    """
    A new requirement definition
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'id': directives.unchanged,
        'prefix': directives.unchanged,
        'label': directives.unchanged,
        'priority': directives.unchanged,
        'allocation': directives.unchanged,
        'owner': directives.unchanged,
        'parent': directives.unchanged,
        'version': directives.unchanged,
        'comment': directives.unchanged,
        'csv-file': directives.path,
        'type': directives.unchanged,
        'category': directives.unchanged,
        'batch': directives.unchanged,
    }

    def run(self):
        # if 'csv-file' in self.options:
        #     # we are importing a bunch of req
        #     relpath, abspath = self.env.relfn2path(directives.path(self.options.get('csv-file')))
        #     self.env.note_dependency(relpath)

        #     del self.options['csv-file']
        #     # label must be unique for one req. Avoid duplication
        #     if 'label' in self.options:
        #         del self.options['label']

        #     # XXX

        reqid = self.options.get('id',None)
        title = None
        
        if self.arguments:
            if reqid:
                title = self.arguments[0]
            else:
                args = self.arguments[0].split('\n')
                if len(args)>0:
                    reqid = args[0]
                    title = '\n'.join(args[1:])
        
        if reqid is None:
            # generate a unique local id
            reqid = '%03d' % (self.env.new_serialno()+1,)

        content='\n'.join(self.content)

        node = xxxreq_node('', **self.options)
        node['reqid'] = reqid
        node['title'] = title
        node['content'] = content

        r = ReSTRenderer(os.path.dirname(__file__))
        kwargs = dict(
                reqid=reqid,
                title=title,
                content=content)
        kwargs.update(self.options)
        s = r.render('req.rst', kwargs)

        nodes = self.parse_text_to_nodes(s)
        return [node]+nodes

def setup(app):
    app.add_directive('xxxreq', XXXReq)
    app.add_node(xxxreq_node,
                 html=(visit_xxxreq_node, depart_xxxreq_node),
                 latex=(latex_visit_xxxreq_node, latex_depart_xxxreq_node))
