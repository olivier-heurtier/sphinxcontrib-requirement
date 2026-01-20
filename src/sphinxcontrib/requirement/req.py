
# https://www.sphinx-doc.org/en/master/development/tutorials/adding_domain.html
# https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain
# https://www.sphinx-doc.org/en/master/development/tutorials/extending_syntax.html#tutorial-extending-syntax

"""
Global process:

- <N/A>: Read all rst documents and build a database of all requirements in the domain
  (domain.data['reqs']) through domain.add_req method
- Once all documents have been read and that domain.data['reqs'] is up-to-date:

  - <env_updated>: Execute reqlist queries and convert to req attribute
  - <env_updated>: process all pseudo attributes (from links) and replace with real values (text or ReqReference)
  - <env_updated>: Add a target node for all ReqReference

  - <doctree-resolved>: Then lastly process all ReqRefReference nodes to point to the corresponding (list of) ReqReference

"""


import io
import os
import csv
import pickle
import textwrap
import re

import jinja2

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.utils import DependencyList
from docutils.io import StringOutput
from docutils.transforms.references import Substitutions

import sphinx
from sphinx.domains import Domain
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.template import SphinxRenderer, ReSTRenderer, LaTeXRenderer
from sphinx.jinja2glue import SphinxFileSystemLoader
from sphinx.util.docutils import sphinx_domains
if sphinx.version_info>=(9,0,0):
    from sphinx.util.docutils import _parse_str_to_doctree
    from sphinx.environment import _CurrentDocument
from sphinx.util import rst
from sphinx.errors import SphinxError

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers import text
from sphinx.builders.text import TextBuilder

# XXX HTML: links local to the page behave differently
# XXX :req:req:`reqid` fails in reqlist content

_DEBUG = False

# typing of directive option to define links (list of IDs)
def link(argument):
    if not argument.strip():
        ret = []
    else:
        ret = [x.strip() for x in argument.split(',')]
    if _DEBUG:
        print('Transforming(link) <%s> -> <%s>' % (argument, ret))
    return ret

#______________________________________________________________________________
class ReqException(Exception):
    pass

#______________________________________________________________________________
class req_links_node(nodes.Element):
    # will contain a reqid and a link name
    pass

class ReqLinks(SphinxRole):
    def run(self): # -> tuple[list[Node], list[system_message]]:
        parts = self.text.split('::')
        opts = {}
        opts['link'] = parts[0]
        opts['reqid'] = parts[1]
        p  = req_links_node('', **opts)
        return ([p], [])

#______________________________________________________________________________
class req_node(nodes.Element):
    pass

def html_visit_req_node(self: HTML5Translator, node: req_node) -> None:
    if 'hidden' not in node.attributes:
        r = SphinxRenderer( [self.builder.app.env.srcdir, os.path.dirname(__file__)] )
        s = r.render('req.html.jinja2', node.attributes)
        v,d = s.split('---CONTENT---')
        self.body.append(v)
        self._req = d

def latex_visit_req_node(self: LaTeXTranslator, node: req_node) -> None:
    if 'hidden' not in node.attributes:
        r = LaTeXRenderer( [self.builder.app.env.srcdir, os.path.dirname(__file__)] )
        s = r.render('req.latex.jinja2', node.attributes)
        v,d = s.split('---CONTENT---')
        self.body.append(v)
        self._req = d


def depart_req_node(self: LaTeXTranslator, node: req_node) -> None:
    if 'hidden' not in node.attributes:
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
        'label': directives.unchanged,  # a text used in replacement of reqid when defining links
        'csv-file': directives.path,
        'filter': directives.unchanged,
        'sort': directives.unchanged,
        'hidden': directives.flag,
    }

    # Transform the directive into a list of docutils nodes
    def run(self):
        # For development
        if _DEBUG:
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'reqlist.rst.jinja2'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.rst.jinja2'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.html.jinja2'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.latex.jinja2'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.preamble'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.css'))
            self.env.note_dependency(os.path.join(os.path.dirname(__file__), 'req.py'))
        self.env.note_dependency(os.path.join(self.env.srcdir, 'req.rst.jinja2'))

        def _create_node(options):
            reqid = options.get('reqid',None)
            if reqid is None:
                # generate a unique local id
                docnames = list(self.env.app.project.docnames)
                docnames.sort()
                doc_idx = docnames.index(self.env.docname)
                # Propose a serial unique in the whole set of documents
                reqid = self.env.config.req_idpattern.format(**dict(doc=doc_idx, doc_serial=self.env.new_serialno('req')+1, serial=self.env.get_domain('req').new_serial()))
            options['reqid'] = reqid
            # create pseudo properties for links, they will be converted later on
            for l, rl in self.env.config.req_links.items():
                options['_'+l] = ':req:links:`{}::{}`'.format(l, reqid)
                options['_'+rl] = ':req:links:`{}::{}`'.format(rl, reqid)

            node = req_node('', **options)

            targetid = 'req-'+reqid
            targetnode = nodes.target('', '', ids=[targetid])
            node += targetnode

            node['ids'].append(targetid)

            def my_wrap(text, width = 80, **kwargs):
                return text.splitlines()

            def _get_text(s):
                builder = TextBuilder(self.env.app, self.env)
                # do not wrap the lines (for long title)
                owrap = text.my_wrap
                text.my_wrap = my_wrap
                writer = text.TextWriter(builder)
                destination = StringOutput(encoding='utf-8')
                doc = nodes.document(self.state.document.settings, self.state.document.reporter )
                doc.substitution_defs = self.state.document.substitution_defs
                doc += self.parse_text_to_nodes(s)
                Substitutions(doc).apply()
                writer.write(doc, destination)
                # restore previous wrap function
                text.my_wrap = owrap
                return writer.output.strip()
            options['text_content'] = node['text_content'] = _get_text(node['content'])
            options['text_title'] = node['text_title'] = _get_text(node['title'])

            if 'hidden' not in options:
                r = ReSTRenderer( [self.env.srcdir,os.path.dirname(__file__)] )
                loader = jinja2.PrefixLoader({
                    '': r.env.loader,
                    'req': SphinxFileSystemLoader([os.path.dirname(__file__)])
                })
                r.env.loader = loader
                s = r.render('/req.rst.jinja2', options)

                sub_nodes = self.parse_text_to_nodes(s)
                node += sub_nodes

            self.env.get_domain('req').add_req(node, self.env.docname)

            return [node]

        if 'csv-file' in self.options:
            # we are importing a bunch of req
            relpath, abspath = self.env.relfn2path(self.options.get('csv-file'))
            self.env.note_dependency(relpath)

            req_filter = None
            sort = None
            del self.options['csv-file']
            if 'filter' in self.options:
                req_filter = self.options['filter']
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
                    raise ReqException("Missing header row in %s" % abspath)
                
                for row in spamreader:
                    options = {}
                    options.update(self.options)
                    for i in range(len(fieldnames)):
                        v = fieldnames[i]
                        if v in ReqDirective.option_spec:
                            options[v] = ReqDirective.option_spec[v](row[i])
                        else:
                            options[v] = row[i]
                    allreqs.append(options)
            # apply filter and sorting
            allreqs = _filter_and_sort(allreqs, req_filter, sort)

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

        # split using a single '|' to extract the comment (if any)
        parts = content.split('\n|\n')
        content = parts[0].strip()
        if len(parts)>1:
            self.options['comment'] = '\n'.join(parts[1:]).strip()
        self.options['title'] = title
        self.options['content'] = content

        return _create_node(self.options)


#______________________________________________________________________________
def _filter_and_sort(reqs :list[req_node], filter :str=None, sort :str=None) -> list[req_node]:
    # transform the filter to a function
    if filter:
        def _filter(r):
            # Since custo attributes may not be defined on all requirements
            # we are trying to set a default value (None) in case of error
            d = dict()
            d.update(globals())
            while True:
                try:
                    x = eval(filter, d, r)
                    return x
                except NameError as exc:
                    if exc.name in ReqDirective.option_spec.keys():
                        d[exc.name] = None
                    else:
                        raise
                else:
                    raise
        ff = _filter
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
                reqs.sort(key=lambda r, key=x: r.get(key[1:], ''), reverse=True)
            else:
                reqs.sort(key=lambda r, key=x: r.get(key, ''), reverse=False)
    return reqs

class reqlist_node(nodes.Element):
    def get_list(self, dom):
        # Get the list of all requirements
        reqs = []
        for data in dom.data['reqs']:
            reqs.append(data[1])

        # filter and sort
        reqs = _filter_and_sort(reqs, self['filter'], self['sort'])
        return reqs

    def fill(self, dom, app, doctree, fromdocname):
        if _DEBUG:
            print('----- fill ----- ' + fromdocname)

        # Get the list of all requirements
        reqs = self.get_list(dom)

        # evaluate the content
        if 'hidden' not in self.attributes:
            r = ReSTRenderer( [app.srcdir, os.path.dirname(__file__)] )
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
                s = r.render('reqlist.rst.jinja2', kwargs)

            document = self.read_doc(app, s)

            # fix docname in all nodes of the document
            # fix also the corresponding data in env
            for node in document.traverse(ReqReference):
                node['refdoc'] = fromdocname

            # fix any ids that could be duplicated due to a local env
            # for now, only with table
            for node in document.traverse(nodes.table):
                if 'ids' in node and node['ids'] and node['ids'][0].startswith('id'):
                    node['ids'] = ['reqlist%d'  % app.env.new_serialno('reqlist')]

            self += document.children

    def read_doc(self, app, s):
        # parse the resulting string (from sphinx.builders.Builder.read_doc)
        # with the directives and roles active

        if sphinx.version_info<(8,0,0):
            app.env.prepare_settings('reqlist.rst')
            publisher = app.registry.get_publisher(app, 'restructuredtext')
            publisher.settings.record_dependencies = DependencyList()
            with sphinx_domains(app.env), rst.default_role('reqlist.rst', app.config.default_role):
                publisher.set_source(source=io.StringIO(s), source_path='reqlist.rst')
                publisher.publish()
                document = publisher.document
        elif sphinx.version_info<(9,0,0):
            # Sphinx 8
            sn = app.env.current_document._serial_numbers
            app.env.prepare_settings('reqlist.rst')
            publisher = app.registry.get_publisher(app, 'restructuredtext')
            publisher.settings.record_dependencies = DependencyList()
            with sphinx_domains(app.env), rst.default_role('reqlist.rst', app.config.default_role):
                publisher.set_source(source=io.StringIO(s), source_path='reqlist.rst')
                publisher.publish()
                document = publisher.document
            app.env.current_document._serial_numbers = sn
        else:
            env  = app.env
            sn = env.current_document._serial_numbers
            env.prepare_settings('reqlist.rst')

            filetype = 'restructuredtext'
            parser = app.registry.create_source_parser(
                filetype, config=app.builder.config, env=env
            )
            doctree = _parse_str_to_doctree(
                s,
                filename='reqlist.rst',
                default_role=app.config.default_role,
                default_settings=env.settings,
                env=env,
                events=app.builder.events,
                parser=parser,
                transforms=app.builder._registry.get_transforms(),
            )
            doctree.reporter = None  # type: ignore[assignment]
            doctree.transformer = None  # type: ignore[assignment]
            document = doctree

            # cleanup
            env.current_document = _CurrentDocument()
            env.ref_context.clear()
            env.current_document._serial_numbers = sn

        return document        

def visit_reqlist_node(self, node: reqlist_node) -> None:
    if 'csv-file' in node.attributes:
        dom = self.builder.env.get_domain('req')
        # Get the list of all requirements
        reqs = node.get_list(dom)

        # dump in a CSV
        fn = node['csv-file']
        fn = os.path.join(self.builder.outdir, fn)
        dirname = os.path.dirname(fn)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(fn, 'wt') as csvfile:
            wr = csv.writer(csvfile, delimiter=',')
            if 'headers' in node.attributes:
                wr.writerow(node['headers'])
            else:
                wr.writerow(node['fields'])
            for r in reqs:
                wr.writerow([r.get(x, '') for x in node['fields']])

def depart_reqlist_node(self, node: reqlist_node) -> None:
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
        'csv-file': directives.path,
        'hidden': directives.flag,
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
        self.env.note_dependency(os.path.join(self.env.srcdir, 'reqlist.rst.jinja2'))

        node = reqlist_node('')

        node['align'] = self.options.get('align', 'left')
        node['header-rows'] = self.options.get('header-rows', '1')
        node['stub-columns'] = self.options.get('stub-columns', '0')
        node['width'] = self.options.get('width', '100%')
        node['widths'] = self.options.get('widths', '20 80')

        node['filter'] = self.options.get('filter',None)
        node['sort'] = self.options.get('sort',None)
        if 'csv-file' in self.options:
            node['csv-file'], dummy = self.env.relfn2path(self.options['csv-file'])
        if 'hidden' in self.options:
            node['hidden'] = None
        node['fields'] = [x.strip() for x in self.options.get('fields','reqid, title').split(',')]
        if 'headers' in self.options:
            node['headers'] = [x.strip() for x in self.options['headers'].split(',')]
        else:
            node['headers'] = node['fields']
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
    return builder.get_relative_uri(fromdocname, todocname)

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
        'links': ReqLinks(),
    }

    initial_data = {
        'reqs': [],  # object list
        'N': 1,
        'serial': 1,
        'reqrefs' : [],
    }
    data_version = 0

    def new_serial(self):
        current = self.data['serial']
        self.data['serial'] = current + 1
        return current

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
        if _DEBUG:
            print('------------- clear_doc %s ----------------' % (docname,) )
            print(len(self.data['reqs']), len(self.data['reqrefs']))
        # remove all objects from docname
        self.data['reqs'] = list(filter(lambda x: x[3]!=docname, self.data['reqs']))
        self.data['reqrefs'] = list(filter(lambda x: x[3]!=docname, self.data['reqrefs']))
        if _DEBUG:
            print(len(self.data['reqs']), len(self.data['reqrefs']))

    def add_req(self, req, docname):
        if _DEBUG:
            print ('Adding req ' + req['reqid'] + ' from ' + docname)

        # reqid MUST be unique
        match = [req2
            for name2, req2, typ2, docname2, anchor2, prio2 in self.data['reqs']
            if req['reqid']==req2['reqid'] or req['reqid']==req2.attributes.get('label', 'LABEL_UNDEF2')
        ]
        if match:
            msg = "Requirement ID must be unique. "+req['reqid']+" was defined multiple times, either as a reqid or as a label"
            raise SphinxError(msg)

        # if defined, label MUST be unique
        if 'label' in req.attributes:
            match = [req2
                for name2, req2, typ2, docname2, anchor2, prio2 in self.data['reqs']
                if req['label']==req2['reqid'] or req['label']==req2.attributes.get('label', 'LABEL_UNDEF2')
            ]
            if match:
                msg = "Requirement label must be unique. "+req['label']+" was defined multiple times, either as a reqid or as a label"
                raise SphinxError(msg)

        name = 'req-'+req['reqid']
        anchor = 'req-'+req['reqid']
        self.data['reqs'].append((
            name,               # the unique key to the requirement (fixed prefix + ID)
            req,                # the node itself
            'req',              # the type of node
            docname,            # the docname for this requirement
            anchor,             # the anchor name, used in reference/target
            0,                  # the priority
        ))

    def add_reqref(self, reqref, target, docname):
        if _DEBUG:
            print ('Adding reqref ' + target + ' from ' + docname)
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
    app.env.note_dependency(os.path.join(app.env.srcdir, 'req.html.jinja2'))
    app.env.note_dependency(os.path.join(app.env.srcdir, 'req.latex.jinja2'))

#______________________________________________________________________________
def env_updated(app, env):
    if _DEBUG:
        print('----------------env-updated-------------------------')
        print('docs: ' + str(env.all_docs.keys()))

    dom = env.get_domain('req')

    # Get a list of defined labels
    # label -> reqid
    labels = { req['label']:req['reqid']
        for name, req, typ, docname, anchor, prio in dom.data['reqs']
        if req.attributes.get('label', None)
    }

    # Execute reqlist queries and convert to req attribute
    for docname in env.all_docs.keys():
        # inspired by Environment.get_and_resolve_doctree
        try:
            doctree = env._write_doc_doctree_cache[docname]
            doctree.settings.env = env
        except KeyError:
            doctree = env.get_doctree(docname)
            env._write_doc_doctree_cache[docname] = doctree

        for node in doctree.traverse(reqlist_node):
            node.fill(dom, app, doctree, docname)

    # process all pseudo attributes (from links) and replace with real values (ReqReference)
    # step 1 - fill attribute values
    # links = {reqid -> {link -> set(ids)}
    links = {}
    link_name = {}
    for l, rl in env.config.req_links.items():
        link_name[l] = rl
        link_name[rl] = l
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        for node in doctree.traverse(req_node):
            for l in link_name:
                for x in node.get(l, []):
                    # if a label, we need to translate
                    if x in labels:
                        x = labels[x]
                    links.setdefault(x, dict()).setdefault(link_name[l], set()).add( node['reqid'] )
                links.setdefault(node['reqid'], dict()).setdefault(l, set()).update( [labels.get(x, x) for x in node.get(l, () )] )
    # apply
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        for node in doctree.traverse(req_node):
            for l in link_name:
                node[l] = list(links[node['reqid']][l])

    # step 2 - do the replacement
    reqrefs_just_added = set()
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        if _DEBUG:
            print('Removing req_links_node from ' + docname)
        for node in doctree.traverse(req_links_node):
            # get the req from the domain data
            p  = nodes.inline(text='')
            match = [req
                for name, req, typ, docname, anchor, prio in dom.data['reqs']
                if req['reqid']==node['reqid']
            ]
            if match and match[0].get(node['link']):
                # build a list of ReqReference
                for r in match[0].get(node['link']):
                    n = ReqReference('', '', internal=True)
                    reqrefs_just_added.add(n)
                    n['reftarget'] = r
                    n['refdoc'] = docname
                    targetid = dom.add_reqref(n, n['reftarget'], n['refdoc'])
                    targetnode = nodes.target('', '', ids=[targetid])
                    n['ids'].append(targetid)
                    n.children = targetnode + n.children

                    n.append( nodes.literal(text=r, classes=['xref', 'req', 'req-req']) )

                    p += n
                    p += nodes.inline(text=', ')
                if p.children:
                    p.pop()
            if not p.children:
                p  = nodes.inline(text='\u202F')
            node.replace_self(p)

    # Do not use label in ReqReference, replace with reqid
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        for node in doctree.traverse(ReqReference):
            # get the target req from the domain data
            match = [
                (docname, anchor, req)
                for name, req, typ, docname, anchor, prio in dom.data['reqs']
                if req.attributes.get('label', 'LABEL_UNDEF') == node['reftarget']
            ]
            if len(match) > 0:
                node['reftarget'] = match[0][2]['reqid']
                if node.children:
                    node.children[0].children[0] = nodes.Text(match[0][2]['reqid'])

    # Apply pattern for text of reference
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        for node in doctree.traverse(ReqReference):
            # get the target req from the domain data
            match = [
                (docname, anchor, req)
                for name, req, typ, docname, anchor, prio in dom.data['reqs']
                if req['reqid'] == node['reftarget']
            ]
            if len(match) > 0:
                req = match[0][2]
                if node.children:
                    s = app.config.req_reference_pattern.format(**req.attributes)
                    node.children[0].children[0] = nodes.Text(s)

    # Do not use label in ReqRefReference
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        for node in doctree.traverse(ReqRefReference):
            match = [
                (docname, anchor, req)
                for name, req, typ, docname, anchor, prio in dom.data['reqs']
                if req.attributes.get('label', 'LABEL_UNDEF') == node['reftarget']
            ]
            if len(match) > 0:
                node['reftarget'] = match[0][2]['reqid']

    # Add a target node for all ReqReference
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]

        for node in doctree.traverse(ReqReference):
            # we process only the ReqReference added by Sphinx after parsing a rst
            # and not the nodes added after replacing a pseudo attribute
            if node in reqrefs_just_added:
                continue
            # populate its attributes so that it can be a target itself
            # and record in the domain this node
            targetid = dom.add_reqref(node, node['reftarget'], node['refdoc'])
            targetnode = nodes.target('', '', ids=[targetid])
            node['ids'].append(targetid)
            node.children = targetnode + node.children

            # refuri will be set in doctree-resolved, once we have identified
            # all the nodes

    # since we will reexecute queries in doctree_resolved
    # we don't want to keep old ReqReference in domain
    # let's reinit completely the list
    dom.data['reqrefs'] = []
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]

        for reqref in doctree.traverse(ReqReference):
            name = reqref['targetid']
            dom.data['reqrefs'].append((
                name,
                reqref,
                'reqref',
                docname,
                name,
                1,
            ))

    # update pickled doctree (Latex builder is starting from the cache of pickled doctree)
    # we need to update env._pickled_doctree_cache[docname]
    # do not save in a file, content would not be purged correctly when read again
    for docname in env.all_docs.keys():
        doctree = env._write_doc_doctree_cache[docname]
        s = pickle.dumps(doctree, pickle.HIGHEST_PROTOCOL)
        env._pickled_doctree_cache[docname] = s
        
    # make sure that all doc are rewritten
    return list(env.all_docs.keys())

#______________________________________________________________________________
def doctree_resolved(app, doctree, fromdocname):
    if _DEBUG:
        print('----------------doctree_resolved--%s-----------------------' % fromdocname)
    dom = app.env.get_domain('req')

    # Now that we have the complete list of requirements (i.e. all source files
    # have been read and all directives executed), we can transform the ReqReference
    # to point to the req_node object
    for node in doctree.traverse(ReqReference):
        if 'refuri' in node:
            continue
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

    # We have now the complete list of ReqReference (references pointing to a requirement)
    # We can transform the ReqRefReference
    # to point to the ReqReference object
    for node in doctree.traverse(ReqRefReference):
        # node['refid'] = node['reftarget']
        # Get all ReqReference nodes, and add a reference to them
        match = [
            (docname, anchor, reqref)
            for name, reqref, typ, docname, anchor, prio in dom.data['reqrefs']
            if reqref['reftarget'] == node['reftarget']
        ]
        p  = nodes.inline()
        for r in match:
            if _DEBUG:
                print("Adding a reference to ReqReference ",node['refdoc'], r[2]['refdoc'], r[1])
            n = nodes.reference('', '', internal=True)
            n['refuri'] = get_refuri(app.builder, node['refdoc'], r[2]['refdoc'], r[1])
            n.append( nodes.inline(text=app.config.req_reference_text) )
            p += n

        node.replace_self(p)
    for node in doctree.traverse(ReqRefReference):
        print('**** ERROR')

#______________________________________________________________________________
def config_inited(app, config):
    if _DEBUG:
        print('----------------config_inited-----------------------')

    # Define roles & HTML styles
    if not config.rst_prolog:
        config.rst_prolog = ''
    config.rst_prolog = '''

.. role:: reqid

.. role:: title

.. raw:: html

    <style>
    ''' + textwrap.indent(config.req_html_css, '        ') + '''
    </style>
    ''' + config.rst_prolog

    # Define LaTeX preamble for envs and styles
    config.latex_elements.setdefault('preamble', '')
    # Give the opportunity to the config preamble to redefine commands or envs
    config.latex_elements['preamble'] = config.req_latex_preamble + config.latex_elements['preamble']

    # Apply customized options & links
    for k,v in config.req_options.items():
        ReqDirective.option_spec[k] = eval(v)

    for l, rl in config.req_links.items():
        ReqDirective.option_spec[l] = link
        ReqDirective.option_spec[rl] = link

#______________________________________________________________________________
def setup(app: Sphinx) -> ExtensionMetadata:
    # config: req_html_style, req_latex_preamble
    if os.path.isfile(os.path.join(app.srcdir, 'req.preamble')):
        with open(os.path.join(app.srcdir, 'req.preamble'), 'r') as f:
            latex_preamble_default = f.read()
    else:
        with open(os.path.join(os.path.dirname(__file__), 'req.preamble'), 'r') as f:
            latex_preamble_default = f.read()
    app.add_config_value('req_latex_preamble', latex_preamble_default, 'env', [str]) # LaTeX preamble added in the config

    if os.path.isfile(os.path.join(app.srcdir, 'req.css')):
        with open(os.path.join(app.srcdir, 'req.css'), 'r') as f:
            html_css_default = f.read()
    else:
        with open(os.path.join(os.path.dirname(__file__), 'req.css'), 'r') as f:
            html_css_default = f.read()
    app.add_config_value('req_html_css', html_css_default, 'env', [str]) # HTML stylesheet

    app.add_config_value('req_reference_text', u'\u2750', 'env', [str]) # Character or string used for cross references
    app.add_config_value('req_options', {}, 'env', [dict]) # Additional options/fields that can be defined on requirements
    app.add_config_value('req_links', {}, 'env', [dict]) # Additional links between requirements
    app.add_config_value('req_idpattern', 'REQ-{doc:02}{doc_serial:03d}', 'env', [str]) # Additional options/fields that can be defined on requirements
    app.add_config_value('req_reference_pattern', '{reqid}', 'env', [str]) # pattern of text inserted when a reference is

    app.connect('config-inited', config_inited)
    app.connect('doctree-read', doctree_read)
    app.connect('env-updated', env_updated)
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