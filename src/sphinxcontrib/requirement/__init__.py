# -*- coding: utf-8 -*-
"""
    sphinxcontrib.requirement
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow requirement definition and references to be inserted into your
    documentation.

"""

# Latex output for requirements / list
# difficult to reference a req that has no id yet. Define a 'label' ?
# XXX make sur all ids (manual or automatic) are unique, at least in the scope of one doc
# define a 'group' option to have multiple (and distinct) id generation scope. Done using the prefix as the group name
# move to a Sphinx package on its own
# provide a "matching pattern" to filter the req included in a list
# directive option to define table widths
# ability to "declare" for one doc the docid to use
# ability to specify the format (concatenation way)
# design a way to "align" all tables used for req display (solution: a style to set the width to 100%)
# XXX Add a span element for the comment section (to allow: hide, background color, etc.)
# matrix should include "references", i.e. links to where the req is referenced. Include section title? No, a simple "arrow" is enough
# XXX add a directive 'req-test' to describe a test case associated to a requirement (requirement is mandatory)

from __future__ import print_function

import re
import csv

import docutils.statemachine
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive

from sphinx.roles import XRefRole
from sphinx.locale import _
from sphinx.errors import NoUri
from sphinx.util.nodes import set_source_info
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
import sphinx.addnodes

STYLE = '''
<style>
   .requirement-comment {
        font-style:italic;
        line-height: 100%;
    }
    
    .requirement-comment * {
        font-style:italic;
        line-height: 100%;
    }
    
    table.requirement {
        width: 100% !important;
        border-left-width: 0px !important;
        border-right-width: 0px !important;
        border-top-width: 0px !important;
        border-bottom-width: 1px !important;
        border-style:solid !important;
        border-color: #E0E0E0 !important;
    }
    
    table.requirement tbody tr td {
        border-width: 0px !important;
        line-height: 100%;
        text-align: justify;
        background-color: transparent !important;
        vertical-align: top !important;        
    }
    
    table.requirement tbody tr td p {
        font-size: 100%;
        border-width: 0px !important;
        line-height: 100%;
        text-align: justify;
    }

    table.requirement tbody tr td * {
        font-size: 100%;
        margin-bottom: 0px;
        margin-top: 2px;
    }

    table.requirement tbody tr td ul {
        margin-bottom: 0px !important;
    }
    
    table.requirement tbody tr td p.admonition-title:after {
        content:"" !important;
    }
    table.requirement tbody tr td p.admonition-title:before {
        content:"" !important;
    }
    table.requirement tbody tr td p.admonition-title {
        background-color: transparent !important;
        color: black !important;
        margin-top: -2px !important;
        padding-top: 0px;        
    }

    table.requirement tbody tr td:nth-child(2) p:first-child {
        margin-top: -2px !important;
    }

    table.requirement-list, table.requirement-list th, table.requirement-list td {
        font-size: 100%;
        border-left-width: 1px !important;
        border-right-width: 1px !important;
        border-top-width: 1px !important;
        border-bottom-width: 1px !important;
        border-style:solid !important;
        border-color: #A0A0A0 !important;
    }

    table.requirement-list p, table.requirement-list ul {
        font-size: 100%;
        margin: 0px !important;
    }        
</style>
'''    

PREFIX = 'REQ'
FORMAT = '%(prefix)s-%(docid)s-%(reqid)s'
DOCID = ''

def build_caption(dir,caption):
    inodes, messages = dir.state.inline_text(caption,
                                             dir.lineno)
    caption_node = nodes.title(caption, '', *inodes)
    caption_node.extend(messages)
    set_source_info(dir, caption_node)
    return caption_node

class reqdeclare_node(nodes.General, nodes.Element):
    pass

class ReqDeclare(Directive):
    """
    Directive to declare requirements parameters
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'prefix': directives.unchanged,
        'format': directives.unchanged,
        'docid': directives.unchanged,
        'widths': directives.positive_int_list,
    }

    def run(self):
        val = self.content
        
        code = '\n'.join(self.content)
        
        node = reqdeclare_node()
        node['prefix'] = self.options.get('prefix',None)
        node['format'] = self.options.get('format',None)
        node['docid'] = self.options.get('docid',None)
        node['widths'] = self.options.get('widths',None)

        global PREFIX
        global FORMAT
        global DOCID
        if node['prefix']:
            PREFIX = node['prefix']
        if node['format']:
            FORMAT = node['format']
        if node['docid']:
            DOCID = node['docid']
        
        return [node]


class req_node(nodes.admonition):
    def get_reference_node(self,app,docname):
        newnode = nodes.reference('', '', internal=True)
        innernode = nodes.inline(text=self.get_reqname(app))
        try:
            newnode['refuri'] = app.builder.get_relative_uri(docname, self['docname'])
            newnode['refuri'] += '#' + self['targetid']
        except NoUri as e:
            print(e)
            # ignore if no URI can be determined, e.g. for LaTeX output
            pass
        newnode.append(innernode)
        return newnode

    def get_reqname(self,app):
        
        # Finish definition of reqname (we need toc_secnumbers correctly initialized)
        # XXX could also generate unique ids here
        #env = app.builder.env
        if not self['reqname']:
            reqid = self['reqid']
            reqname = FORMAT % {'prefix':self.get('prefix',PREFIX),'docid':DOCID,'reqid':reqid}
            self['reqname'] = reqname
        return self['reqname']
    
    def is_target(self,app,target):
        if self['label']==target or self.get_reqname(app)==target or self['reqid']==target:
            return True
        return False
    
class req_ref(nodes.reference):
    def get_reference_node(self,app,docname):
        newnode = nodes.reference('', '', internal=True)
        # See http://character-code.com/arrows-html-codes.php
        # diamond: \u2662
        # 3D box: \u2750
        # arrow: \u2192 
        innernode = nodes.inline(text=u'\u2750')
        try:
            newnode['refuri'] = app.builder.get_relative_uri(docname, self['docname'])
            newnode['refuri'] += '#' + self['targetid']
        except NoUri as e:
            print(e)
            # ignore if no URI can be determined, e.g. for LaTeX output
            pass
        newnode.append(innernode)
        return newnode

class ReqAdmonition(BaseAdmonition):

    node_class = req_node

class Req(Directive):
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
        env = self.state.document.settings.env
        if 'csv-file' in self.options:
            # we are importing a bunch of req
            rel_filename, filename = env.relfn2path(self.options.get('csv-file'))
            env.note_dependency(rel_filename)
            del self.options['csv-file']
            # label must be unique for one req. Avoid duplication
            if 'label' in self.options:
                del self.options['label']
            
            # Read the csv
            allnodes = []
            with open(filename, 'rt') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';')
                fieldnames = next(spamreader)
                if not 'text' in fieldnames:
                    raise Exception("Missing header row in %s" % filename)
                
                for row in spamreader:
                    self.content = None
                    for i in range(len(fieldnames)):
                        v = fieldnames[i]
                        if v=='text':
                            self.content = docutils.statemachine.StringList(row[i].splitlines(), source=filename)
                        elif v=='comment':
                            pass
                        else:
                            self.options[v] = row[i]
                    for i in range(len(fieldnames)):
                        v = fieldnames[i]
                        if self.content and v=='comment' and row[i].strip():
                            self.content.append( docutils.statemachine.StringList( ['','|',''] + row[i].splitlines(), source=filename) )
                    allnodes.extend(self.run())
            return allnodes

        newid = self.options.get('id',None)
        title = None
        
        if self.arguments:
            if newid:
                title = self.arguments[0]
            else:
                args = self.arguments[0].split('\n')
                if len(args)>0:
                    newid = args[0]
                if len(args)>0:
                    title = '\n'.join(args[1:])
        
        if newid:
            reqid = newid
            reqname = newid
        else:
            # generate a unique local id
            reqid = '%03d' % (env.new_serialno(self.options.get('prefix',PREFIX+'-'+DOCID))+1,)
            reqname = None # will be built first time it is needed
            
        targetid = 'req-'+self.options.get('prefix',PREFIX+'-'+DOCID+'-')+reqid
        targetnode = nodes.target('', '', ids=[targetid])

        # title will be replaced later on
        try:
            ad = ReqAdmonition(self.name, [_('Requirement')], self.options,
                                 self.content, self.lineno, self.content_offset,
                                 self.block_text, self.state, self.state_machine).run()
        except:
            print(self.content)
            raise
        set_source_info(self, ad[0])
        ad[0]['reqid'] = reqid
        ad[0]['targetid'] = targetid
        ad[0]['reqname'] = reqname
        if 'prefix' in self.options:
            ad[0]['prefix'] = self.options['prefix']
        ad[0]['title'] = title
        ad[0]['priority'] = self.options.get('priority',None)
        ad[0]['allocation'] = self.options.get('allocation',None)
        ad[0]['owner'] = self.options.get('owner',None)
        ad[0]['parent'] = self.options.get('parent',None)
        ad[0]['version'] = self.options.get('version',None)
        ad[0]['label'] = self.options.get('label','')
        ad[0]['type'] = self.options.get('type',None)
        ad[0]['category'] = self.options.get('category',None)
        ad[0]['batch'] = self.options.get('batch',None)
        ad[0]['docname'] = env.docname
        ad[0]['reqname'] = ad[0].get_reqname(None)
        blk = None
        for n in ad[0]:
            if isinstance(n,nodes.line_block):
                blk = n
            elif blk:
                n['classes'].extend(['requirement-comment'])
        if blk:
            ad[0].remove(blk)
            
        
        for node in ad[0].traverse(req_ref):
            node.replace_self( nodes.Text( node['reftarget'] ) )
        
            
        return [targetnode] + ad

class reqlist_node(nodes.General, nodes.Element): pass

class ReqList(Directive):
    """
    A list of all requirements.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'caption': directives.unchanged,
        'pattern': directives.unchanged,
        'widths': directives.positive_int_list,
        'headers': directives.unchanged,
        'fields': directives.unchanged,
        'sort': directives.unchanged,
       
        }

    def run(self):
        # Simply insert an empty reqlist node which will be replaced later
        # when process_req_nodes is called
        
        node = reqlist_node('')
        node['caption'] = self.options.get('caption',None)
        if 'caption' in self.options:
            node += build_caption(self,self.options['caption'])
        node['pattern'] = self.options.get('pattern','')
        node['widths'] = self.options.get('widths',[15,10,15,85])
        node['headers'] = [x.strip() for x in self.options.get('headers','ID, Priority, Allocation, Description').split(',')]
        node['fields'] = [x.strip() for x in self.options.get('fields','id, priority, allocation, text').split(',')]
        node['sort'] = self.options.get('sort',None)

        if node['sort'] and not node['sort'] in node['fields']:
            for fs in re.split('[, ]+',node['sort']):
                if fs not in node['fields']:
                    raise Exception("Invalid sort option '" + node['sort'] + "' (must include one of the selected fields: '"+str(node['fields'])+"')")
        
        return [node]


def doctree_read(app, doctree):

    # collect all requirements in the environment
    # this is not done in the directive itself because some transformations
    # must have already been run, e.g. substitutions
    env = app.builder.env
    if not hasattr(env, 'req_all_reqs'):
        env.req_all_reqs = []
    for node in doctree.traverse(req_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError
        except IndexError:
            targetnode = None
        env.req_all_reqs.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'req': node.deepcopy(),
            'target': targetnode,
            'label': node['label'],
        })

    # Collect all refs
    if not hasattr(env, 'req_all_refs'):
        env.req_all_refs = []
    N = 0
    for node in doctree.traverse(req_ref):
        N += 1
        targetid = 'ref-%05d' % N
        node['ids'].append(targetid)
        node['docname'] = env.docname
        node['targetid'] = targetid
        env.req_all_refs.append({
            'docname': env.docname,
            'ref': node,
            'targetid':targetid,
            'reftarget':node['reftarget']
        })

    # process labels so that ref role can extract the table caption
    docname = env.temp_data['docname']
    document = doctree
    self = env.domains['std']

    # Copy and adapted from sphinx.domains.std.process_doc
    if 1:
        labels, anonlabels = self.data['labels'], self.data['anonlabels']
        for name, explicit in document.nametypes.items():
            if not explicit:
                continue
            labelid = document.nameids[name]
            if labelid is None:
                continue
            node = document.ids[labelid]
            if name.isdigit() or 'refuri' in node or \
                   node.tagname.startswith('desc_'):
                # ignore footnote labels, labels automatically generated from a
                # link and object descriptions
                continue
            if name in labels:
                continue
            anonlabels[name] = docname, labelid
            if node.tagname == 'reqlist_node':
                if not 'caption' in node:
                    continue
                sectname = node['caption']
            else:
                # anonymous-only labels
                continue
            labels[name] = docname, labelid, sectname

def doctree_resolved(app, doctree, fromdocname):

    # Replace all reqlist nodes with a list of the collected requirements.
    # Augment each requirement with a backlink to the original location.
    env = app.builder.env
    
    if isinstance(doctree,nodes.document):
        attributes = {'format': 'html'}
        doctree.insert(0,nodes.raw('', STYLE, **attributes))
    
    if not hasattr(env, 'req_all_reqs'):
        env.req_all_reqs = []
    if not hasattr(env, 'req_all_refs'):
        env.req_all_refs = []

    REQ_WIDTHS = [10,20,20,20,20]
    
    def get_references(req):
        # for the given link, find all references to it
        ret = []
        for ref in env.req_all_refs:
            if req.is_target(app,ref['reftarget']):
                ret.append( ref['ref'].get_reference_node(app,fromdocname) )
        return ret
    
    def get_reference_node(target):
        for req_info in env.req_all_reqs:
            req = req_info['req']
            if req.is_target(app,target):
                return req.get_reference_node(app,fromdocname)
                break
        else:
            try:
                return nodes.Text(node['reftarget']) # XXX node?
            except:
                return nodes.Text(target)
    
    for node in doctree.traverse(lambda x: isinstance(x, reqdeclare_node) or isinstance(x,reqlist_node) or isinstance(x,req_node)):
        if isinstance(node,reqdeclare_node):
            if node['prefix']:
                PREFIX = node['prefix']
            if node['format']:
                FORMAT = node['format']
            if node['docid']:
                DOCID = node['docid']
            if node['widths']:
                REQ_WIDTHS = node['widths']
                if len(REQ_WIDTHS)==2:
                    REQ_WIDTHS = [REQ_WIDTHS[0],REQ_WIDTHS[1]/4,REQ_WIDTHS[1]/4,REQ_WIDTHS[1]/4,REQ_WIDTHS[1]/4]
            node.parent.remove(node)

        if isinstance(node,reqlist_node):
            content = []

            # Insert a table
            
            if node['pattern']:
                pattern = re.compile(node['pattern'])
            else:
                pattern = None

            # generate table-root
            if len(node['widths'])!=len(node['headers']) or len(node['headers'])!=len(node['fields']):
                raise Exception('Invalid configuration, inconsistent number of colums')
            tgroup = nodes.tgroup(cols=len(node['headers']))
            for width in node['widths']:
                tgroup += nodes.colspec(colwidth=width)
            table = nodes.table()
            doctree.set_id(table)
            table['classes'] += ['requirement-list','longtable']
            table['classes'].append('colwidths-given')
            table += tgroup

            # generate table-header
            thead = nodes.thead()
            row = nodes.row()
            for header in node['headers']:
                entry = nodes.entry()
                entry += nodes.paragraph(text=header)
                row += entry
            thead += row
            tgroup += thead

            # generate rows
            tbody = nodes.tbody()
            for req_info in env.req_all_reqs:
                reqname = req_info['req'].get_reqname(app)
                if pattern and not pattern.search(reqname):
                    continue
                
                row = nodes.row()
                row['reqname'] = reqname

                # ['id','priority','allocation','text']
                for f in node['fields']:
                    if f=='id':
                        # One cell for the name with a link to the definition
                        entry = nodes.entry()
                        p = nodes.paragraph()
                        p += req_info['req'].get_reference_node(app,fromdocname)
                        entry += p
                        row += entry
                    elif f=='text':
                        # One cell for the text of the requirement (without the title)
                        entry = nodes.entry()
                        p = nodes.paragraph('','',*req_info['req'][0:])
                        # resolve the pending_xref that could be part of the description
                        # since the same nodes is used in different docname context, we need
                        # to update the refdoc attribute (Bug DOCPRODUCTION-257)
                        for node_xref in p.traverse(lambda x: isinstance(x, sphinx.addnodes.pending_xref)):
                            node_xref['refdoc'] = fromdocname
                        env.resolve_references(p, fromdocname, app.builder)
                        entry += p
                        row += entry
                        row['reqtext'] = str(p)
                    elif f=='children':
                        # find all req that have this one on their parents
                        # XXX To be optimized
                        entry = nodes.entry()
                        p = nodes.paragraph()
                        for req_info2 in env.req_all_reqs:
                            if req_info2['req']['parent']:
                                l = req_info2['req']['parent'].split(',')
                                for t in l:
                                    if req_info['req'].is_target(app,t.strip()):
                                        p += nodes.Text(', ')
                                        p += req_info2['req'].get_reference_node(app,fromdocname)
                                        break
                        if len(p)>0:
                            del p[0]
                        else:
                            p = nodes.paragraph(text='')
                        entry += p
                        row += entry
                        row['reqchildren'] = str(p)
                    elif f=='references':
                        entry = nodes.entry()
                        p = nodes.paragraph()
                        entry += p
                        row += entry
                        p += get_references(req_info['req'])
                        row['reqreferences'] = str(p)
                    elif f=='parent':
                        entry = nodes.entry()
                        p = nodes.paragraph()
                        if req_info['req'][f]:
                            l = req_info['req'][f].split(',')
                            for t in l:
                                if t.strip():
                                    p += nodes.Text(', ')
                                    p += get_reference_node(t.strip())
                            if len(p)>0:
                                del p[0]
                        else:
                            p = nodes.paragraph(text='')
                        entry += p
                        row['reqparent'] = str(p)
                        row += entry
                    else:
                        entry = nodes.entry()
                        try:
                            v = req_info['req'][f]
                        except:
                            v = None
                        if v:
                            p = nodes.paragraph(text=v)
                        else:
                            p = nodes.paragraph(text='')
                        entry += p
                        row += entry
                        row[f] = v

                tbody += row

            # Sort the table                
            if node['sort']:
                fs_list = list( re.split('[, ]+',node['sort']) )
                if 'id' in fs_list: fs_list[fs_list.index('id')] = 'reqname'
                if 'text' in fs_list: fs_list[fs_list.index('text')] = 'reqtext'
                if 'children' in fs_list: fs_list[fs_list.index('children')] = 'reqchildren'
                if 'references' in fs_list: fs_list[fs_list.index('references')] = 'reqreferences'
                if 'parent' in fs_list: fs_list[fs_list.index('parent')] = 'reqparent'
            else:
                fs_list = ['reqname']
            def sortkey(a):
                return '--'.join([a[x] for x in fs_list])
            tbody.children.sort(key=sortkey)
            tgroup += tbody
            
            if node['caption']:
                caption = node[0]
                node.remove(caption)
                table.append(caption)
            
            node.replace_self([table])
            
        if isinstance(node,req_node):
            
            if app.builder.name=="latex":
                table = ReqLatexTable()
                table.col_widths = REQ_WIDTHS
                table.node_id = nodes.paragraph(text=node.get_reqname(app))
                if node['title']:
                    table.node_title = nodes.paragraph(text=node['title'])
                table.node_text = nodes.container()
                table.node_text += node[0:]
                table.node_refs = get_references(node)
                if node['parent']:
                    l = node['parent'].split(',')
                    if l:
                        table.node_parent = nodes.paragraph()
                        for t in l:
                            if t.strip():
                                table.node_parent += nodes.Text(', ')
                                table.node_parent += get_reference_node(t.strip())
                        del table.node_parent[0]
                if node['priority']:
                    table.node_priority = nodes.paragraph(text='Priority: '+node['priority'])
                if node['allocation']:
                    table.node_allocation = nodes.paragraph(text='Allocation: '+node['allocation'])
                if node['version']:
                    table.node_version = nodes.paragraph(text='Version: '+node['version'])
                if node['owner']:
                    table.node_owner = nodes.paragraph(text='Owner: '+node['owner'])
                if node['type']:
                    table.node_type = nodes.paragraph(text='Type: '+node['type'])
                if node['category']:
                    table.node_category = nodes.paragraph(text='Category: '+node['category'])
                if node['batch']:
                    table.node_batch = nodes.paragraph(text='Batch: '+node['batch'])
                node.replace_self(table)
                continue
            
            # Replace title with the full requirement name
            table = nodes.table()
            doctree.set_id(table)
            table['classes'] += ['requirement']
            table['classes'].append('colwidths-given')
            tgroup = nodes.tgroup(cols=5)
            for width in REQ_WIDTHS:
                tgroup += nodes.colspec(colwidth=width)
            table += tgroup

            # generate rows
            tbody = nodes.tbody()
            tgroup += tbody

            # id + title and text
            row = nodes.row()
            tbody += row

            entry = nodes.entry()
            entry['morerows'] = 3
            row += entry
            entry += nodes.paragraph(text=node.get_reqname(app),classes=['admonition-title'])
            
            entry = nodes.entry()
            row += entry
            entry['morecols'] = 3
            if node['title']:
                entry += nodes.paragraph(text=node['title'])

                row = nodes.row()
                tbody += row
                entry = nodes.entry()
                entry['morecols'] = 3
                row += entry
            entry += node[0:]

            refs = get_references(node)
            force_break = False
            if refs:
                p = entry[-1]
                if not isinstance(p,nodes.paragraph) or 'requirement-comment' in p['classes']:
                    entry += nodes.paragraph()
                    force_break = True
                entry[-1] += nodes.Text(" (")
                entry[-1] += refs
                entry[-1] += nodes.Text(")")
            
            if node['parent']:
                p = entry[-1]
                if force_break or not isinstance(p,nodes.paragraph) or 'requirement-comment' in p['classes']:
                    p = nodes.paragraph()
                    entry += p
                p += nodes.Text("[")
                pos = len(p)
                l = node['parent'].split(',')
                for t in l:
                    p += nodes.Text(', ')
                    p += get_reference_node(t.strip())
                del p[pos]
                p += nodes.Text("]")
                
            # Priority + allocation
            if node['priority'] or node['allocation'] or node['version'] or node['owner']:
                row = nodes.row()
                tbody += row

                entry = nodes.entry()
                row += entry
                if node['priority']:
                    entry += nodes.paragraph(text='Priority: '+node['priority'])

                entry = nodes.entry()
                row += entry
                if node['allocation']:
                    entry += nodes.paragraph(text='Allocation: '+node['allocation'])

                entry = nodes.entry()
                row += entry
                if node['version']:
                    entry += nodes.paragraph(text='Version: '+node['version'])

                entry = nodes.entry()
                row += entry
                if node['owner']:
                    entry += nodes.paragraph(text='Owner: '+node['owner'])

            # Type and category
            if node['type'] or node['category'] or node['batch']:
                row = nodes.row()
                tbody += row

                entry = nodes.entry()
                row += entry
                if node['type']:
                    entry += nodes.paragraph(text='Type: '+node['type'])

                entry = nodes.entry()
                row += entry
                if node['category']:
                    entry += nodes.paragraph(text='Category: '+node['category'])

                entry = nodes.entry()
                row += entry
                if node['batch']:
                    entry += nodes.paragraph(text='Batch: '+node['batch'])

                entry = nodes.entry()
                row += entry

            node.replace_self([table,nodes.paragraph()])

    for node in doctree.traverse(req_ref):
        node.replace_self(get_reference_node(node['reftarget']))
        
#
# Custom output for requirement when using the Latex builder
#

class ReqLatexTable(nodes.General, nodes.Element):
    # Custom table for Latex output
    col_widths = []
    node_id = None
    node_title = None
    node_text = nodes.container()
    node_refs = []
    node_parent = None
    node_priority = None
    node_allocation = None
    node_version = None
    node_owner = None
    node_type = None
    node_category = None
    node_batch = None
    
def cleaneol(l,pos):
    # remove all \n between pos and -1
    i = pos
    while i<len(l):
        while i<len(l) and l[i]=='\n':
            del l[i]
        i += 1
    
def visit_req_latex_table(self, node):
    # use the widths
    total =sum(node.col_widths)
    p0 = node.col_widths[0]/float(total)
    p1 = 1.0 - p0 - 0.05
    self.body.append("\n\n\\begin{tabulary}{\\linewidth}{p{%f\\linewidth}p{%f\\linewidth}}" % (p0,p1))
    self.body.append('\\textbf{\\hspace{-.1cm}'+self.encode(node.node_id.astext())+'}')
    self.body.append(r" & ")
    if node.node_title:
        node.append(node.node_title)
        node.node_title.walkabout(self)
        node.remove(node.node_title)
    comment = False
    for n in node.node_text:
        if isinstance(n,nodes.paragraph) and 'requirement-comment' in n['classes'] and not comment:
            self.body.append('\\par\\begin{itshape}')
            comment = True
        n.walkabout(self)
    if comment:
        self.body.append('\\end{itshape}')
    if node.node_refs:
        self.body.append('(')
        pos = len(self.body)
        for r in node.node_refs:
            r.walkabout(self)
        self.body.append(')')
        cleaneol(self.body,pos)
        self.body.append('\n')
    if comment:
        self.body.append('\n')
    if node.node_parent:
        self.body.append('[')
        pos = len(self.body)
        node.append(node.node_parent)
        node.node_parent.walkabout(self)
        node.remove(node.node_parent)
        self.body.append(']')
        cleaneol(self.body,pos)
    self.body.append("\\\\ \n")
    if node.node_priority or node.node_allocation or node.node_version or node.node_owner \
            or node.node_type or node.node_category or node.node_batch:
        self.body.append('&\n')
        self.body.append('\\begin{small}\n')

        total =sum(node.col_widths)
        p1 = node.col_widths[1]/float(total)
        p2 = node.col_widths[2]/float(total)
        p3 = node.col_widths[3]/float(total)
        p4 = node.col_widths[4]/float(total)
        self.body.append('\\begin{tabular*}{1.0\\linewidth}{p{%f\\linewidth}p{%f\\linewidth}p{%f\\linewidth}p{%f\\linewidth} }' % (p1,p2,p3,p4) )

        self.body.append('\\\\ \n \\hline \n')
        if node.node_priority or node.node_allocation or node.node_version or node.node_owner:
            pos = len(self.body)
            if node.node_priority:
                node.append(node.node_priority)
                node.node_priority.walkabout(self)
                node.remove(node.node_priority)
            self.body.append('&')
            if node.node_allocation:
                node.append(node.node_allocation)
                node.node_allocation.walkabout(self)
                node.remove(node.node_allocation)
            self.body.append('&')
            if node.node_version:
                node.append(node.node_version)
                node.node_version.walkabout(self)
                node.remove(node.node_version)
            self.body.append('&')
            if node.node_owner:
                node.append(node.node_owner)
                node.node_owner.walkabout(self)
                node.remove(node.node_owner)
            cleaneol(self.body,pos)
            self.body.append('\\\\ \n \\hline \n')
        
        if node.node_type or node.node_category or node.node_batch:
            pos = len(self.body)
            if node.node_type:
                node.append(node.node_type)
                node.node_type.walkabout(self)
                node.remove(node.node_type)
            self.body.append('&')
            if node.node_category:
                node.append(node.node_category)
                node.node_category.walkabout(self)
                node.remove(node.node_category)
            self.body.append('&')
            if node.node_batch:
                node.append(node.node_batch)
                node.node_batch.walkabout(self)
                node.remove(node.node_batch)
            self.body.append('&')
            cleaneol(self.body,pos)
            self.body.append('\\\\ \n \\hline \n')
        
        self.body.append('\\end{tabular*}\n\n')

        self.body.append('\\end{small}\n')
            
    self.body.append('\\end{tabulary}\n\n')
    
    raise nodes.SkipNode
def purge_reqs(app, env, docname):
    if hasattr(env, 'req_all_reqs'):
        env.req_all_reqs = [req for req in env.req_all_reqs
                          if req['docname'] != docname]

    if hasattr(env, 'req_all_refs'):
        env.req_all_refs = [ref for ref in env.req_all_refs
                          if ref['docname'] != docname]

    # reset global settings, defined with a config option or with a declare directive
    global PREFIX
    global FORMAT
    global DOCID
    PREFIX = app.builder.config.req_prefix
    FORMAT = '%(prefix)s-%(docid)s-%(reqid)s'
    DOCID = '%03d' % env.toc_secnumbers.get(docname,{}).get('',(0,))[0]

# Patch latex writer
# In Latex, the Sphinx writer adds extra spaces around the hyperlink
# they appear as spaces in the output and generate spaces and indentation in tables
import sphinx.writers.latex
old_visit = sphinx.writers.latex.LaTeXTranslator.visit_reference
def new_visit(self, node):
    if self.table:
        self.context.append(len(self.body))
    return old_visit(self,node)
sphinx.writers.latex.LaTeXTranslator.visit_reference = new_visit

old_depart = sphinx.writers.latex.LaTeXTranslator.depart_reference
def new_depart(self, node):
    ret = old_depart(self,node)
    if self.table:
        pos = self.context.pop()
        cleaneol(self.body,pos)
    return ret
sphinx.writers.latex.LaTeXTranslator.depart_reference = new_depart

def setup(app):
    app.add_config_value('req_prefix', 'REQ', 'env')

    app.add_node(reqlist_node)
    app.add_node(req_node)
    app.add_node(reqdeclare_node)

    app.add_directive('req', Req)
    app.add_directive('req-list', ReqList)
    app.add_directive('req-declare', ReqDeclare)
    app.add_node(req_ref)
    app.add_role('req', XRefRole(nodeclass=req_ref))
    app.connect('doctree-read', doctree_read)
    app.connect('doctree-resolved', doctree_resolved)
    app.connect('env-purge-doc', purge_reqs)

    app.add_node(ReqLatexTable,
                 latex=(visit_req_latex_table, None))
