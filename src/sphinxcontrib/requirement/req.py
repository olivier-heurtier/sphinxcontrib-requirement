
# https://www.sphinx-doc.org/en/master/development/tutorials/adding_domain.html
# https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain
# https://www.sphinx-doc.org/en/master/development/tutorials/extending_syntax.html#tutorial-extending-syntax

import io
import os
import csv
import textwrap
from typing import TYPE_CHECKING, Any, ClassVar, cast

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.domains import Domain
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective
from sphinx.util.template import ReSTRenderer, LaTeXRenderer
from sphinx.util.docutils import sphinx_domains
from docutils.utils import DependencyList
from sphinx.util import rst

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator

# XXX bad links

_DEBUG = False

# typing of directive option
def link(argument):
    ret = [x.strip() for x in argument.split(',')]
    if _DEBUG:
        print('Transforming(link) [%s] -> [%s]' % (argument, ret))
    return ret

# filter in Jinja templates
def links_filter(value):
    if type(value) in [list, tuple]:
        ret = ', '.join([f':req:req:`{x}`' for x in value])
    elif type(value) is str and value:
        v = value.strip()
        ret = f':req:req:`{v}`'
    else:
        ret = ''
    if _DEBUG:
        print('Transforming(filter) [%s] -> [%s]' % (value, ret))
    return ret
#______________________________________________________________________________
class req_node(nodes.Element):
    pass

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
        'reqid': directives.unchanged,
        'csv-file': directives.path,
        'filter': directives.unchanged,
        'sort': directives.unchanged,
    }

    # XXX define comment separated with | 
    # Transform the directive into a list of docutils nodes
    def run(self):
        # For development
        if _DEBUG:
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'reqlist.rst'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.rst'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.html'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.latex'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.preamble'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.css'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.py'))

        def _create_node(options):
            reqid = options.get('reqid',None)
            if reqid is None:
                # generate a unique local id
                reqid = self.env.config.req_idpattern.format(self.env.new_serialno('req')+1)
            options['reqid'] = reqid

            node = req_node('', **options)

            targetid = 'req-'+reqid
            targetnode = nodes.target('', '', ids=[targetid])
            node += targetnode

            node['ids'].append(targetid)

            r = ReSTRenderer(os.path.dirname(__file__))
            r.env.filters['links'] = links_filter
            s = r.render('req.rst', options)

            sub_nodes = self.parse_text_to_nodes(s)
            node += sub_nodes

            self.env.get_domain('req').add_req(node)

            return [node]

        if 'csv-file' in self.options:
            # we are importing a bunch of req
            relpath, abspath = self.env.relfn2path(self.options.get('csv-file'))
            self.env.note_dependency(relpath)

            filter = None
            sort = None
            del self.options['csv-file']
            if 'filter' in self.options:
                filter = self.options['filter']
                del self.options['filter']
            if 'sort' in self.options:
                sort = self.options['sort']
                del self.options['sort']

            # Read the csv
            allreqs = []
            with open(abspath, 'rt') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                fieldnames = next(spamreader)
                if 'reqid' not in fieldnames and 'title' not in fieldnames and 'content' not in fieldnames:
                    raise Exception("Missing header row in %s" % abspath)
                
                for row in spamreader:
                    options = {}
                    options.update(self.options)
                    for i in range(len(fieldnames)):
                        v = fieldnames[i]
                        options[v] = row[i]
                    allreqs.append(options)
            # apply filter and sorting
            allreqs = _filter_and_sort(allreqs, filter, sort)

            # create the nodes for the remaining requirements
            allnodes = []
            for req_options in allreqs:
                allnodes.extend(_create_node(req_options))
            return allnodes

        # only used if csv-file, ignore otherwise
        if 'filter' in self.options:
            del self.options['filter']
        if 'sort' in self.options:
            del self.options['sort']

        title = ''
        if self.arguments:
            title = self.arguments[0]
        if self.content:
            content='\n'.join(self.content)
        else:
            content=''
        self.options['title'] = title
        self.options['content'] = content

        return _create_node(self.options)


#______________________________________________________________________________
def _filter_and_sort(reqs :list[req_node], filter :str=None, sort :str=None) -> list[req_node]:
    # transform the filter to a function
    if filter:
        ff = lambda r: eval(filter, dict(), r)
    else:
        ff = lambda r: True

    # Filter the input list
    new_reqs = []
    for req in reqs:
        if ff(req):
            new_reqs.append(req)
    reqs = new_reqs

    # sort the result
    if sort:
        fs_list = [x.strip() for x in sort.split(',')]
        for x in fs_list:
            if x and x[0]=='-':
                reqs.sort(key=lambda r: r.get(x[1:], ''), reverse=True)
            else:
                reqs.sort(key=lambda r: r.get(x, ''), reverse=False)
    return reqs

from copy import copy

class reqlist_node(nodes.Element):
    def fill(self, dom, app, doctree, fromdocname):
        if _DEBUG:
            print('----- fill -----')

        # Get the list of all requirements
        reqs = []
        for data in dom.data['reqs']:
            reqs.append(data[1])

        # filter and sort
        reqs = _filter_and_sort(reqs, self['filter'], self['sort'])

        # evaluate the content
        r = ReSTRenderer(os.path.dirname(__file__))
        r.env.filters['links'] = links_filter
        kwargs = dict(
            reqs=reqs,
            caption=self['caption'],
            align=self['align'],
            width=self['width'],
            widths=self['widths'],
            header_rows=self['header-rows'],
            stub_columns=self['stub-columns'],
            fields=self['fields'],
            headers=self['headers'],
        )
        if self['content']:
            s = r.render_string(self['content'], kwargs)
        else:
            s = r.render('reqlist.rst', kwargs)

        # parse the resulting string (from sphinx.builders.Builder.read_doc)
        # with the directives and roles active
        app.builder.env.prepare_settings('reqlist.rst')
        publisher = app.registry.get_publisher(app, 'restructuredtext')
        app.builder.env.temp_data['_parser'] = publisher.parser
        publisher.settings.record_dependencies = DependencyList()
        with sphinx_domains(app.env), rst.default_role('reqlist.rst', app.config.default_role):
            publisher.set_source(source=io.StringIO(s), source_path='reqlist.rst')
            publisher.publish()
            document = publisher.document
        # cleanup
        app.builder.env.temp_data.clear()
        app.builder.env.ref_context.clear()

        # fix docname in all nodes of the document
        # fix also the corresponding data in env
        for node in document.traverse(ReqReference):
            node['refdoc'] = fromdocname
        
        document.children[0]['ids'] = [str(app.env.new_serialno())] # XXXX needed?
        # XXX eliminate XRefNode???
        self += document.children


def visit_reqlist_node(self, node: reqlist_node) -> None:
    return

def depart_reqlist_node(self: LaTeXTranslator, node: reqlist_node) -> None:
    return

class ReqListDirective(SphinxDirective):
    """
    A list of requirements.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'filter': directives.unchanged,
        'sort': directives.unchanged,
        'headers': directives.unchanged,
        'fields': directives.unchanged,
        'align': directives.unchanged,
        'header-rows': directives.unchanged,
        'stub-columns': directives.unchanged,
        'width': directives.unchanged,
        'widths': directives.unchanged,
        }

    def run(self):
        # Simply insert an empty reqlist node which will be replaced later
        # when process_req_nodes is called
        
        node = reqlist_node('')

        node['align'] = self.options.get('align', 'left')
        node['header-rows'] = self.options.get('header-rows', '1')
        node['stub-columns'] = self.options.get('stub-columns', '0')
        node['width'] = self.options.get('width', '100%')
        node['widths'] = self.options.get('widths', '20 80')

        node['filter'] = self.options.get('filter',None)
        node['sort'] = self.options.get('sort',None)
        node['headers'] = [x.strip() for x in self.options.get('headers','ID, Title').split(',')]
        node['fields'] = [x.strip() for x in self.options.get('fields','reqid, title').split(',')]
        caption = ''
        if self.arguments:
            caption = self.arguments[0]
        node['caption'] = caption
        node['content'] = '\n'.join(self.content)
        return [node]

#______________________________________________________________________________
def get_refuri(builder, fromdocname, todocname, target):
    if target:
        return builder.get_relative_uri(fromdocname, todocname) + '#' + target
    else:
        return builder.get_relative_uri(fromdocname, todocname)
    return target

#______________________________________________________________________________
class ReqReference(nodes.reference):
    pass

#______________________________________________________________________________
class ReqRefReference(nodes.reference):
    pass

#______________________________________________________________________________
class ReqDomain(Domain):
    name = 'req'
    label = 'Requirement Management'

    directives = {
        'req': ReqDirective,
        'reqlist': ReqListDirective,
    }
    roles = {
        'req': XRefRole(nodeclass=ReqReference),
        'ref': XRefRole(nodeclass=ReqRefReference),
    }

    initial_data = {
        'reqs': [],  # object list
        'N': 1,
        'reqrefs' : [],
    }
    data_version = 0

    def get_full_qualified_name(self, node):
        if type(node) is ReqReference:
            return 'req-'+node['reqid']
        if type(node) is ReqRefReference:
            return 'req-ref-'+node['reqid']
        return node['reqid']

    def get_objects(self):
        for x in self.data['reqs']:
            yield (x[0], x[1]['reqid'], x[2], x[3], x[4], x[5])

    def clear_doc(self, docname):
        # remove all objects from docname
        self.data['reqs'] = list(filter(lambda x: x[3]!=docname, self.data['reqs']))
        self.data['reqrefs'] = list(filter(lambda x: x[3]!=docname, self.data['reqrefs']))

    def add_req(self, req):
        if _DEBUG:
            print ('Adding req ' + req['reqid'])
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

    def add_reqref(self, reqref, target, docname):
        if _DEBUG:
            print ('Adding reqref ' + target)
        name = target + '-' + '%06d'%self.data['N']
        self.data['N'] += 1
        reqref['targetid'] = name
        self.data['reqrefs'].append((
            name,
            reqref,
            'reqref',
            docname,
            name,
            1,
        ))
        return name

#______________________________________________________________________________
def doctree_read(app, doctree):
    if _DEBUG:
        print('----------------doctree_read-------------------------')
    dom = app.env.get_domain('req')
    # we are calculating and setting the target for ReqReference
    for node in doctree.traverse(ReqReference):
        # populate its attributes so that it can be a target itself
        # and record in the domain this node
        targetid = dom.add_reqref(node, node['reftarget'], node['refdoc'])
        targetnode = nodes.target('', '', ids=[targetid])
        node['ids'].append(targetid)
        node.children = targetnode + node.children

        # refuri will be set in doctree-resolved, once we have identified
        # all the nodes

#______________________________________________________________________________
def doctree_resolved(app, doctree, fromdocname):
    if _DEBUG:
        print('----------------doctree_resolved--%s-----------------------' % fromdocname)
    dom = app.env.get_domain('req')

    # execute the query for each reqlist
    for node in doctree.traverse(reqlist_node):
        node.fill(dom, app, doctree, fromdocname)

    # Expand the reverse links (example: children) if any
    rlinks = {}
    for k, v in app.env.config.req_links.items():
        rlinks[v] = k
    if _DEBUG:
        print('rlinks: ', rlinks)
    for node in doctree.traverse(ReqReference):
        parts = node['reftarget'].split('::')
        if len(parts)==2 and parts[0] in rlinks:
            if _DEBUG:
                print('rlinks: parts:', parts)
            # calculate
            match = [
                (docname, anchor, req)
                for name, req, typ, docname, anchor, prio in dom.data['reqs']
                if parts[1] in req.get(rlinks[parts[0]],[])
            ]
            if _DEBUG:
                print('rlinks: match:', match)
            # replace this reference with a list of references
            p  = nodes.inline()
            for r in match:
                if _DEBUG:
                    print('  rlinks: ', r[2]['reqid'])
                n = ReqReference('', '', internal=True)

                n['reftarget'] = r[2]['reqid']
                n['refdoc'] = r[0]
                targetid = dom.add_reqref(n, n['reftarget'], n['refdoc'])
                targetnode = nodes.target('', '', ids=[targetid])
                n['ids'].append(targetid)
                n.children = targetnode + n.children

                n.append( nodes.literal(text=r[2]['reqid'], classes=['xref', 'req', 'req-req']) )

                p += n
                p += nodes.inline(text=', ')
            if match:
                p.pop()
            node.replace_self(p)


    # Now that we have the complete list of requirements (i.e. all source files
    # have been read and all directives executed), we can transform the ReqReference
    # to point to the req_node object
    for node in doctree.traverse(ReqReference):
        # get the target req from the domain data
        match = [
            (docname, anchor, req)
            for name, req, typ, docname, anchor, prio in dom.data['reqs']
            if req['reqid'] == node['reftarget']
        ]
        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]
            node['refuri'] = get_refuri(app.builder, fromdocname, todocname, targ)

    # We have also the complete list of ReqReference (references pointing to a requirement)
    # This was loaded while reading the source documents
    # We can transform the ReqRefReference
    # to point to the ReqReference object
    for node in doctree.traverse(ReqRefReference):
        node['refid'] = node['reftarget']
        # Get all ReqReference nodes, and add a reference to them
        match = [
            (docname, anchor, reqref)
            for name, reqref, typ, docname, anchor, prio in dom.data['reqrefs']
            if reqref['reftarget'] == node['reftarget']
        ]
        p  = nodes.inline()
        for r in match:
            n = nodes.reference('', '', internal=True)
            n['refuri'] = get_refuri(app.builder, node['refdoc'], r[2]['refdoc'], r[1])
            n.append( nodes.inline(text=app.config.req_reference_text) )
            p += n
        del node[0]
        node += [p]

#______________________________________________________________________________
def config_inited(app, config):
    if _DEBUG:
        print('----------------config_inited-----------------------')
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

    for k,v in config.req_options.items():
        ReqDirective.option_spec[k] = eval(v)

    for l in config.req_links.keys():
        ReqDirective.option_spec[l] = link

#______________________________________________________________________________
def setup(app: Sphinx) -> ExtensionMetadata:
    # config: req_html_style, req_latex_preamble
    with open(os.path.join(os.path.dirname(__file__), 'req.preamble'), 'r') as f:
        latex_preamble_default = f.read()
    app.add_config_value('req_latex_preamble', latex_preamble_default, 'env', [str], 'LaTeX preamble added in the config')
    with open(os.path.join(os.path.dirname(__file__), 'req.css'), 'r') as f:
        html_css_default = f.read()
    app.add_config_value('req_html_css', html_css_default, 'env', [str], 'HTML stylesheet')
    app.add_config_value('req_reference_text', u'\u2750', 'env', [str], 'Character or string used for cross references')
    app.add_config_value('req_options', {}, 'env', [dict], 'Additional options/fields that can be defined on requirements')
    app.add_config_value('req_links', {}, 'env', [dict], 'Additional links between requirements')
    app.add_config_value('req_idpattern', 'REQ-{:04d}', 'env', [str], 'Additional options/fields that can be defined on requirements')
    # XXX css as a file + possibility to customize the rst, html, latex

    app.connect('config-inited', config_inited)
    app.connect('doctree-read', doctree_read)
    app.connect('doctree-resolved', doctree_resolved)

    app.add_domain(ReqDomain)
    app.add_node(req_node,
                 html= (html_visit_req_node, depart_req_node),
                 latex=(latex_visit_req_node, depart_req_node)
                 )
    app.add_node(reqlist_node,
                 html= (visit_reqlist_node, depart_reqlist_node),
                 latex=(visit_reqlist_node, depart_reqlist_node)
                 )

    return {
        'version': '0.1'
    }