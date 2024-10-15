
# https://www.sphinx-doc.org/en/master/development/tutorials/adding_domain.html
# https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain
# https://www.sphinx-doc.org/en/master/development/tutorials/extending_syntax.html#tutorial-extending-syntax

import os
import textwrap
from typing import TYPE_CHECKING, Any, ClassVar, cast

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from sphinx.domains import Domain
from sphinx.util import texescape
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.template import ReSTRenderer, LaTeXRenderer
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.nodes import make_refnode
from sphinx.errors import NoUri

from collections.abc import Set

from docutils.nodes import Element, Node

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.typing import ExtensionMetadata, OptionSpec
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator

#______________________________________________________________________________
class req_node(nodes.Element):
    # Get a node pointing to this requirement
    def get_reference_node(self, builder, fromdocname, todocname, target, contnode):
        return make_refnode(builder, fromdocname, todocname, self['targetid'], contnode)

def html_visit_req_node(self: HTML5Translator, node: req_node) -> None:
    r = ReSTRenderer(os.path.dirname(__file__))
    s = r.render('req.html', node.attributes)
    v,d = s.split('---CONTENT---')
    self.body.append(v)
    self._req = d

def latex_visit_req_node(self: LaTeXTranslator, node: req_node) -> None:
    r = LaTeXRenderer(os.path.dirname(__file__))
    s = r.render('req.latex', node.attributes)
    v,d = s.split('---CONTENT---')
    self.body.append(v)
    self._req = d


def depart_req_node(self: LaTeXTranslator, node: req_node) -> None:
    self.body.append(self._req)
    self._req = None

class ReqDirective(SphinxDirective):
    """
    A requirement definition
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

    # Transform the directive into a list of docutils nodes
    def run(self):
        # XXX For development
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.rst'))
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.html'))
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.latex'))
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.preamble'))
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.css'))
        self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.py'))

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

        node = req_node('', **self.options)
        node['reqid'] = reqid
        node['title'] = title
        node['content'] = content

        targetid = 'req-'+reqid # self.options.get('prefix',PREFIX+'-'+DOCID+'-')+reqid
        node['ids'].append(targetid)
        node['targetid'] = targetid

        r = ReSTRenderer(os.path.dirname(__file__))
        kwargs = dict(
                reqid=reqid,
                title=title,
                content=content)
        kwargs.update(self.options)
        s = r.render('req.rst', kwargs)

        sub_nodes = self.parse_text_to_nodes(s)
        node += sub_nodes

        self.env.get_domain('req').add_req(node)

        return [node]

#______________________________________________________________________________
class ReqRole(nodes.reference):
    pass
    # def get_reference_node(self,app,docname):
    #     newnode = nodes.reference('', '', internal=True)
    #     # See http://character-code.com/arrows-html-codes.php
    #     # diamond: \u2662
    #     # 3D box: \u2750
    #     # arrow: \u2192 
    #     innernode = nodes.inline(text=u'\u2750')
    #     try:
    #         newnode['refuri'] = app.builder.get_relative_uri(docname, self['docname'])
    #         newnode['refuri'] += '#' + self['targetid']
    #     except NoUri as e:
    #         print(e)
    #         # ignore if no URI can be determined, e.g. for LaTeX output
    #         pass
    #     newnode.append(innernode)
    #     return newnode

#______________________________________________________________________________
class ReqDomain(Domain):
    name = 'req'
    label = 'Requirement Management'

    directives = {
        'req': ReqDirective,
    }
    roles = {
        'req': XRefRole(), #nodeclass=ReqRole),
    }

    initial_data = {
        'reqs': [],  # object list
    }
    data_version = 0

    def get_full_qualified_name(self, node):
        return 'req-'+node['reqid']

    def get_objects(self):
        for x in self.data['reqs']:
            yield (x[0], x[1]['reqid'], x[2], x[3], x[4], x[5])
        # yield from self.data['reqs']

    def add_req(self, req):
        name = 'req-'+req['reqid']
        anchor = 'req-'+req['reqid']
        self.data['reqs'].append((
            name,               # the unique key to the requirement (fixed prefix + ID)
            req,                # the node itself
            'req',              # the type of node
            self.env.docname,   # the docname for this requirement
            anchor,             # the anchor name, used in reference/target
            0,                  # the priority
        ))

    # Transform XRefNode 'node' to a reference that points to a requirement
    def resolve_xref(self, env,
            fromdocname,        # docname where the link is
            builder,
            typ,                # the type of node, as registered in the domain
            target,             # the target text
            node,               # the XRefNode node
            contnode):          # the content of the XRefNode
        match = [
            (docname, anchor, req)
            for name, req, typ, docname, anchor, prio in self.data['reqs']
            if req['reqid'] == target
        ]
        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]
            newnode = match[0][2].get_reference_node(builder,fromdocname, todocname, targ, contnode)
            return newnode
        else:
            return None


def config_inited(app, config):
    if not config.rst_prolog:
        config.rst_prolog = ''
    config.rst_prolog += '''
.. raw:: html

    <style>
    ''' + textwrap.indent(config.req_html_css, '        ') + '''
    </style>
    '''
    config.latex_elements.setdefault('preamble', '')
    config.latex_elements['preamble'] += config.req_latex_preamble

def setup(app: Sphinx) -> ExtensionMetadata:
    # config: req_html_style, req_latex_preamble
    with open(os.path.join(os.path.dirname(__file__), 'req.preamble'), 'r') as f:
        latex_preamble_default = f.read()
    app.add_config_value('req_latex_preamble', latex_preamble_default, 'env', [str], 'LaTeX preamble added in the config')
    with open(os.path.join(os.path.dirname(__file__), 'req.css'), 'r') as f:
        html_css_default = f.read()
    app.add_config_value('req_html_css', html_css_default, 'env', [str], 'HTML stylesheet')
    app.connect('config-inited', config_inited)

    app.add_domain(ReqDomain)
    app.add_node(req_node,
                 html= (html_visit_req_node, depart_req_node),
                 latex=(latex_visit_req_node, depart_req_node))

