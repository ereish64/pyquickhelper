"""
@file
@brief Helpers to convert docstring to various format

.. versionadded:: 1.3
"""
import sys
from collections import deque
import types
import warnings
from sphinx.locale import _
from docutils.parsers.rst import directives, roles
from docutils.languages import en as docutils_en
from sphinx.writers.html import HTMLWriter
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx.environment import BuildEnvironment
from docutils import nodes
from docutils.utils import Reporter
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen
from sphinx.util.docutils import WarningStream
from sphinx.util import status_iterator, logging
from sphinx.transforms import SphinxTransformer
from sphinx.util.osutil import relative_uri
from sphinx.util.logging import getLogger
from ..sphinxext.sphinx_bigger_extension import visit_bigger_node as ext_visit_bigger_node, depart_bigger_node as ext_depart_bigger_node
from ..sphinxext.sphinx_blocref_extension import visit_blocref_node as ext_visit_blocref_node, depart_blocref_node as ext_depart_blocref_node
from ..sphinxext.sphinx_blog_extension import visit_blogpost_node as ext_visit_blogpost_node, depart_blogpost_node as ext_depart_blogpost_node
from ..sphinxext.sphinx_blog_extension import visit_blogpostagg_node as ext_visit_blogpostagg_node, depart_blogpostagg_node as ext_depart_blogpostagg_node
from ..sphinxext.sphinx_exref_extension import visit_exref_node as ext_visit_exref_node, depart_exref_node as ext_depart_exref_node
from ..sphinxext.sphinx_faqref_extension import visit_faqref_node as ext_visit_faqref_node, depart_faqref_node as ext_depart_faqref_node
from ..sphinxext.sphinx_mathdef_extension import visit_mathdef_node as ext_visit_mathdef_node, depart_mathdef_node as ext_depart_mathdef_node
from ..sphinxext.sphinx_nbref_extension import visit_nbref_node as ext_visit_nbref_node, depart_nbref_node as ext_depart_nbref_node
from ..sphinxext.sphinx_runpython_extension import visit_runpython_node as ext_visit_runpython_node, depart_runpython_node as ext_depart_runpython_node
from ..sphinxext.sphinx_sharenet_extension import visit_sharenet_node as ext_visit_sharenet_node, depart_sharenet_node as ext_depart_sharenet_node
from ..sphinxext.sphinx_todoext_extension import visit_todoext_node as ext_visit_todoext_node, depart_todoext_node as ext_depart_todoext_node


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sphinx.builders.html import SingleFileHTMLBuilder

try:
    from sphinx.util.docutils import is_html5_writer_available
    from sphinx.util.docutils import directive_helper
except ImportError:

    from docutils.parsers.rst import convert_directive_function

    # Available only after Sphinx >= 1.6.1.
    def is_html5_writer_available():
        return False

    # from
    # https://github.com/sphinx-doc/sphinx/blob/master/sphinx/util/docutils.py#L162
    def directive_helper(obj, has_content=None, argument_spec=None, **option_spec):
        if isinstance(obj, (types.FunctionType, types.MethodType)):
            obj.content = has_content                       # type: ignore
            obj.arguments = argument_spec or (0, 0, False)  # type: ignore
            obj.options = option_spec                       # type: ignore
            return convert_directive_function(obj)
        else:
            if has_content or argument_spec or option_spec:
                raise ExtensionError(_('when adding directive classes, no '
                                       'additional arguments may be given'))
            return obj

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO

if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
else:
    from sphinx.writers.html import HTMLTranslator


def update_docutils_languages(values=None):
    """
    update ``docutils/languages/en.py`` with missing labels

    does that for languages:

    * en

    @param      values      consider values in this dictionaries first
    """
    if values is None:
        values = dict()
    lab = docutils_en.labels
    if 'versionmodified' not in lab:
        lab['versionmodified'] = values.get(
            'versionmodified', 'modified version')
    if 'desc' not in lab:
        lab['desc'] = values.get('desc', 'description')


class HTMLTranslatorWithCustomDirectives(HTMLTranslator):
    """
    @see cl HTMLWriterWithCustomDirectives
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        HTMLTranslator.__init__(self, builder, *args, **kwds)
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)

    def visit_blogpost_node(self, node):
        """
        @see fn visit_blogpost_node
        """
        ext_visit_blogpost_node(self, node)

    def depart_blogpost_node(self, node):
        """
        @see fn depart_blogpost_node
        """
        ext_depart_blogpost_node(self, node)

    def visit_blogpostagg_node(self, node):
        """
        @see fn visit_blogpostagg_node
        """
        ext_visit_blogpostagg_node(self, node)

    def depart_blogpostagg_node(self, node):
        """
        @see fn depart_blogpostagg_node
        """
        ext_depart_blogpostagg_node(self, node)

    def visit_runpython_node(self, node):
        """
        @see fn visit_runpython_node
        """
        ext_visit_runpython_node(self, node)

    def depart_runpython_node(self, node):
        """
        @see fn depart_runpython_node
        """
        ext_depart_runpython_node(self, node)

    def visit_sharenet_node(self, node):
        """
        @see fn visit_sharenet_node
        """
        ext_visit_sharenet_node(self, node)

    def depart_sharenet_node(self, node):
        """
        @see fn depart_sharenet_node
        """
        ext_depart_sharenet_node(self, node)

    def visit_bigger_node(self, node):
        """
        @see fn visit_bigger_node
        """
        ext_visit_bigger_node(self, node)

    def depart_bigger_node(self, node):
        """
        @see fn depart_bigger_node
        """
        ext_depart_bigger_node(self, node)

    def visit_todoext_node(self, node):
        """
        @see fn visit_todoext_node
        """
        ext_visit_todoext_node(self, node)

    def depart_todoext_node(self, node):
        """
        @see fn depart_todoext_node
        """
        ext_depart_todoext_node(self, node)

    def visit_mathdef_node(self, node):
        """
        @see fn visit_mathdef_node
        """
        ext_visit_mathdef_node(self, node)

    def depart_mathdef_node(self, node):
        """
        @see fn depart_mathdef_node
        """
        ext_depart_mathdef_node(self, node)

    def visit_blocref_node(self, node):
        """
        @see fn visit_blocref_node
        """
        ext_visit_blocref_node(self, node)

    def depart_blocref_node(self, node):
        """
        @see fn depart_blocref_node
        """
        ext_depart_blocref_node(self, node)

    def visit_faqref_node(self, node):
        """
        @see fn visit_faqref_node
        """
        ext_visit_faqref_node(self, node)

    def depart_faqref_node(self, node):
        """
        @see fn depart_faqref_node
        """
        ext_depart_faqref_node(self, node)

    def visit_nbref_node(self, node):
        """
        @see fn visit_nbref_node
        """
        ext_visit_nbref_node(self, node)

    def depart_nbref_node(self, node):
        """
        @see fn depart_nbref_node
        """
        ext_depart_nbref_node(self, node)

    def visit_exref_node(self, node):
        """
        @see fn visit_exref_node
        """
        ext_visit_exref_node(self, node)

    def depart_exref_node(self, node):
        """
        @see fn depart_exref_node
        """
        ext_depart_exref_node(self, node)

    def add_secnumber(self, node):
        """
        overwrites this method to catch errors due when
        it is a single document being processed
        """
        if node.get('secnumber'):
            HTMLTranslator.add_secnumber(self, node)
        elif len(node.parent['ids']) > 0:
            HTMLTranslator.add_secnumber(self, node)
        else:
            n = len(self.builder.secnumbers)
            node.parent['ids'].append("custom_label_%d" % n)
            HTMLTranslator.add_secnumber(self, node)

    def visit_pending_xref(self, node):
        # type: (nodes.Node) -> None
        self.visit_Text(node)
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError("[HTMLTranslatorWithCustomDirectives] Unknown node: '{0}' in '{1}'".format(node.__class__.__name__,
                                                                                                             self.__class__.__name__))


class HTMLWriterWithCustomDirectives(HTMLWriter):
    """
    This docutils writer extends the HTML writer with
    custom directives implemented in this module,
    @see cl RunPythonDirective, @see cl BlogPostDirective

    See `Write your own ReStructuredText-Writer <http://www.arnebrodowski.de/blog/write-your-own-restructuredtext-writer.html>`_.

    This class needs to tell *docutils* to calls the added function
    when directives *RunPython* or *BlogPost* are met.
    """

    def __init__(self, app=None):
        """
        constructor

        @param      app     Sphinx application

        ..versionchanged:: 1.5
            Parameter *app* was added.
        """
        if app is None:
            self.app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                     buildername='memoryhtml')
        else:
            self.app = app
        builder = self.app.builder
        builder.fignumbers = {}
        HTMLWriter.__init__(self, builder)
        self.translator_class = HTMLTranslatorWithCustomDirectives
        self.translator_class = self.translator_class
        self.builder.secnumbers = {}
        self.builder._function_node = []
        self.builder.current_docname = None

    def connect_directive_node(self, name, f_visit, f_depart):
        """
        add custom node to the translator

        @param      name        name of the directive
        @param      f_visit     visit function
        @param      f_depart    depart function
        """
        self.builder._function_node.append((name, f_visit, f_depart))

    def add_configuration_options(self, new_options):
        """
        add new options

        @param      new_options     new options
        """
        for k, v in new_options.items():
            self.builder.config.values[k] = new_options[k]

    def write(self, document, destination):
        """
        Process a document into its final form.

        Translate `document` (a Docutils document tree) into the Writer's
        native format, and write it out to its `destination` (a
        `docutils.io.Output` subclass object).

        Normally not overridden or extended in subclasses.
        """
        # trans = self.builder.create_translator(self.builder, document)
        # if not isinstance(trans, HTMLTranslatorWithCustomDirectives):
        #     raise TypeError("The translator is not of a known type but '{0}'".format(type(trans)))
        HTMLWriter.write(self, document, destination)

    def translate(self):
        # type: () -> None
        # sadly, this is mostly copied from parent class
        self.visitor = visitor = HTMLTranslatorWithCustomDirectives(
            self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        for attr in ('head_prefix', 'stylesheet', 'head', 'body_prefix',
                     'body_pre_docinfo', 'docinfo', 'body', 'fragment',
                     'body_suffix', 'meta', 'title', 'subtitle', 'header',
                     'footer', 'html_prolog', 'html_head', 'html_title',
                     'html_subtitle', 'html_body', ):
            setattr(self, attr, getattr(visitor, attr, None))
        self.clean_meta = ''.join(visitor.meta[2:])


class MemoryHTMLBuilder(SingleFileHTMLBuilder):
    """
    Builds HTML output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
    """
    name = 'memoryhtml'
    format = 'html'
    out_suffix = None  # ".memory.html"
    supported_image_types = ['application/pdf', 'image/png', 'image/jpeg']
    default_translator_class = HTMLTranslatorWithCustomDirectives
    translator_class = HTMLTranslatorWithCustomDirectives
    _writer_class = HTMLWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):
        """
        Construct the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        SingleFileHTMLBuilder.__init__(self, app)
        self.built_pages = {}

    def iter_pages(self):
        """
        Enumerate created pages.

        @return     iterator on tuple(name, content)
        """
        for k, v in self.built_pages.items():
            yield k, v.getvalue()

    def create_translator(self, *args):
        """
        Return an instance of translator.
        This method returns an instance of ``default_translator_class`` by default.
        Users can replace the translator class with ``app.set_translator()`` API.
        """
        translator_class = MemoryHTMLBuilder.translator_class
        return translator_class(*args)

    def _write_serial(self, docnames):
        """
        Overwrite *_write_serial* to avoid writing on disk.
        """
        with logging.pending_warnings():
            for docname in status_iterator(docnames, 'writing output... ', "darkgreen",
                                           len(docnames), self.app.verbosity):
                doctree = self.env.get_and_resolve_doctree(docname, self)
                self.write_doc_serialized(docname, doctree)
                self.write_doc(docname, doctree)

    def _write_parallel(self, docnames, nproc):
        """
        Not supported.
        """
        raise NotImplementedError(
            "Use parallel=0 when creating the sphinx application.")

    def assemble_doctree(self):
        """
        Overwrite *assemble_doctree* to control the doctree.
        """
        master = self.config.master_doc
        if hasattr(self, "doctree_"):
            tree = self.doctree_
        else:
            raise AttributeError(
                "Attribute 'doctree_' is not present. Call method finalize().")
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master
        self.env.resolve_references(tree, master, self)
        self.fix_refuris(tree)
        return tree

    def fix_refuris(self, tree):
        """
        Overwrite *fix_refuris* to control the reference names.
        """
        fname = "__" + self.config.master_doc + "__"
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue
            hashindex = refuri.find('#', hashindex + 1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]

    def get_target_uri(self, docname, typ=None):
        """
        Overwrite *get_target_uri* to control the page name.
        """
        # type: (unicode, unicode) -> unicode
        if docname in self.env.all_docs:
            # all references are on the same page...
            return self.config.master_doc + '#document-' + docname
        elif docname in ("genindex", "search"):
            return self.config.master_doc + '-#' + docname
        else:
            raise KeyError(
                "docname='{0}' should be in self.env.all_docs".format(docname))

    def get_outfilename(self, pagename):
        """
        Overwrite *get_target_uri* to control file names.
        """
        return "{0}/{1}.m.html".format(self.outdir, pagename).replace("\\", "/")

    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        ctx = self.globalcontext.copy()
        ctx['warn'] = self.warn
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        ctx['encoding'] = self.config.html_output_encoding
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        def pathto(otheruri, resource=False, baseuri=default_baseuri):
            # type: (unicode, bool, unicode) -> unicode
            if resource and '://' in otheruri:
                # allow non-local resources given by scheme
                return otheruri
            elif not resource:
                otheruri = self.get_target_uri(otheruri)
            uri = relative_uri(baseuri, otheruri) or '#'
            if uri == '#' and not self.allow_sharp_as_current_path:
                uri = baseuri
            return uri
        ctx['pathto'] = pathto

        def hasdoc(name):
            # type: (unicode) -> bool
            if name in self.env.all_docs:
                return True
            elif name == 'search' and self.search:
                return True
            elif name == 'genindex' and self.get_builder_config('use_index', 'html'):
                return True
            return False
        ctx['hasdoc'] = hasdoc

        ctx['toctree'] = lambda **kw: self._get_local_toctree(pagename, **kw)
        self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        self.update_page_context(pagename, templatename, ctx, event_arg)
        newtmpl = self.app.emit_firstresult('html-page-context', pagename,
                                            templatename, ctx, event_arg)
        if newtmpl:
            templatename = newtmpl

        try:
            output = self.templates.render(templatename, ctx)
        except UnicodeError:
            logger = getLogger("MockSphinxApp")
            logger.warning("[MockSphinxApp] A unicode error occurred when rendering the page %s. "
                           "Please make sure all config values that contain "
                           "non-ASCII content are Unicode strings.", pagename)
            return

        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        # outfilename's path is in general different from self.outdir
        # ensuredir(path.dirname(outfilename))
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(output)


class _CustomBuildEnvironment(BuildEnvironment):
    """
    Overrides some functionalities of
    `BuildEnvironment <http://www.sphinx-doc.org/en/stable/extdev/envapi.html>`_.
    """

    def __init__(self, app):
        """
        """
        BuildEnvironment.__init__(self, app)
        self.doctree_ = {}

    def get_doctree(self, docname):
        # type: (unicode) -> nodes.Node
        """Read the doctree for a file from the pickle and return it."""
        if hasattr(self, "doctree_") and docname in self.doctree_:
            doctree = self.doctree_[docname]
            doctree.settings.env = self
            doctree.reporter = Reporter(self.doc2path(
                docname), 2, 5, stream=WarningStream())
            return doctree
        else:
            raise KeyError("Unable to find doctree for '{0}'.".format(docname))
            # return BuildEnvironment.get_doctree(self, docname)

    def apply_post_transforms(self, doctree, docname):
        # type: (nodes.Node, unicode) -> None
        """Apply all post-transforms."""
        # set env.docname during applying post-transforms
        self.temp_data['docname'] = docname

        transformer = SphinxTransformer(doctree)
        transformer.set_environment(self)
        transformer.add_transforms(self.app.post_transforms)
        transformer.apply_transforms()
        self.temp_data.clear()


class _CustomSphinx(Sphinx):
    """
    custom sphinx application to avoid using disk
    """

    def __init__(self, srcdir, confdir, outdir, doctreedir, buildername="memoryhtml",
                 confoverrides=None, status=None, warning=None,
                 freshenv=False, warningiserror=False, tags=None, verbosity=0,
                 parallel=0):
        '''
        constructor

        Some insights about domains:

        ::

            {'cpp': sphinx.domains.cpp.CPPDomain,
             'js': sphinx.domains.javascript.JavaScriptDomain,
             'std': sphinx.domains.std.StandardDomain,
             'py': sphinx.domains.python.PythonDomain,
             'rst': sphinx.domains.rst.ReSTDomain,
             'c': sphinx.domains.c.CDomain}

        And builders:

        ::

            {'epub': ('epub', 'EpubBuilder'),
            'singlehtml': ('html', 'SingleFileHTMLBuilder'),
            'qthelp': ('qthelp', 'QtHelpBuilder'),
            'epub3': ('epub3', 'Epub3Builder'),
            'man': ('manpage', 'ManualPageBuilder'),
            'dummy': ('dummy', 'DummyBuilder'),
            'json': ('html', 'JSONHTMLBuilder'),
            'html': ('html', 'StandaloneHTMLBuilder'),
            'xml': ('xml', 'XMLBuilder'),
            'texinfo': ('texinfo', 'TexinfoBuilder'),
            'devhelp': ('devhelp', 'DevhelpBuilder'),
            'web': ('html', 'PickleHTMLBuilder'),
            'pickle': ('html', 'PickleHTMLBuilder'),
            'htmlhelp': ('htmlhelp', 'HTMLHelpBuilder'),
            'applehelp': ('applehelp', 'AppleHelpBuilder'),
            'linkcheck': ('linkcheck', 'CheckExternalLinksBuilder'),
            'dirhtml': ('html', 'DirectoryHTMLBuilder'),
            'latex': ('latex', 'LaTeXBuilder'),
            'text': ('text', 'TextBuilder'),
            'changes': ('changes', 'ChangesBuilder'),
            'websupport': ('websupport', 'WebSupportBuilder'),
            'gettext': ('gettext', 'MessageCatalogBuilder'),
            'pseudoxml': ('xml', 'PseudoXMLBuilder')}
        '''
        from sphinx.application import Tags, builtin_extensions
        from sphinx.application import Config, CONFIG_FILENAME, ConfigError, VersionRequirementError
        from sphinx import __display_version__

        try:
            from sphinx.registry import SphinxComponentRegistry
            from sphinx.events import EventManager
            from sphinx.extension import verify_required_extensions
        except ImportError:
            from sphinx.application import events
            # Available only after Sphinx >= 1.6.1

            class SphinxComponentRegistry:
                pass

            class EventManager:
                pass

            def verify_required_extensions(*l):
                return True

        # own purpose (to monitor)
        self._added_objects = []

        # from sphinx.domains.cpp import CPPDomain
        # from sphinx.domains.javascript import JavaScriptDomain
        # from sphinx.domains.python import PythonDomain
        # from sphinx.domains.std import StandardDomain
        # from sphinx.domains.rst import ReSTDomain
        # from sphinx.domains.c import CDomain

        if doctreedir is None:
            doctreedir = "."
        if srcdir is None:
            srcdir = "."
        update_docutils_languages()
        self.verbosity = verbosity

        # type: Dict[unicode, Extension]
        self.extensions = {}
        self._setting_up_extension = ['?']      # type: List[unicode]
        self.builder = None                     # type: Builder

        self.registry = SphinxComponentRegistry()
        self.enumerable_nodes = {}              # type: Dict[nodes.Node, Tuple[unicode, Callable]]  # NOQA
        self.post_transforms = []               # type: List[Transform]
        self.html_themes = {}                   # type: Dict[unicode, unicode]

        self.srcdir = srcdir
        self.confdir = confdir
        self.outdir = outdir
        self.doctreedir = doctreedir
        self.parallel = parallel

        if status is None:
            self._status = StringIO()      # type: IO
            self.quiet = True
        else:
            self._status = status
            self.quiet = False

        if warning is None:
            self._warning = StringIO()     # type: IO
        else:
            self._warning = warning
        self._warncount = 0
        self.warningiserror = warningiserror

        self.events = EventManager()

        # keep last few messages for traceback
        # This will be filled by sphinx.util.logging.LastMessagesWriter
        self.messagelog = deque(maxlen=10)  # type: deque

        # say hello to the world
        self.info(bold('Running Sphinx v%s' % "CUSTOM 1.6"))

        # status code for command-line application
        self.statuscode = 0

        # read config
        self.tags = Tags(tags)
        self.config = Config(confdir, CONFIG_FILENAME,
                             confoverrides or {}, self.tags)
        self.sphinx__display_version__ = __display_version__

        # create the environment
        self.env = _CustomBuildEnvironment(self)

        # Changes for Sphinx >= 1.6
        if __display_version__ >= "1.6":
            self.config.check_unicode()
            self.config.pre_init_values()
        else:
            self.config.check_unicode(self.warn)
            self.config.pre_init_values(self.warn)
            self._extensions = {}
            self._events = events.copy()
            self._translators = {}

            update_docutils_languages()
            self.verbosity = verbosity
            self.next_listener_id = 0
            self._extensions = {}
            self._extension_metadata = {}
            self._additional_source_parsers = {}
            self._listeners = {}
            self._setting_up_extension = ['?']
            self.domains = {}
            self.buildername = buildername
            self.builderclasses = dict(memoryhtml=MemoryHTMLBuilder)
            self.enumerable_nodes = {}

        # set up translation infrastructure
        self._init_i18n()

        # check the Sphinx version if requested
        if self.config.needs_sphinx and self.config.needs_sphinx > __display_version__:
            raise VersionRequirementError(
                _('This project needs at least Sphinx v%s and therefore cannot '
                  'be built with this version.') % self.config.needs_sphinx)

        # set confdir to srcdir if -C given (!= no confdir); a few pieces
        # of code expect a confdir to be set
        if self.confdir is None:
            self.confdir = self.srcdir

        # load all built-in extension modules
        for extension in builtin_extensions:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", category=DeprecationWarning)
                    self.setup_extension(extension)
            except Exception as e:
                mes = "Unable to setup_extension '{0}'\nWHOLE LIST\n{1}".format(
                    extension, "\n".join(builtin_extensions))
                raise Exception(mes) from e

        # extension loading support for alabaster theme
        # self.config.html_theme is not set from conf.py at here
        # for now, sphinx always load a 'alabaster' extension.
        if 'alabaster' not in self.config.extensions:
            self.config.extensions.append('alabaster')

        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)

        # add default HTML builders
        self.add_builder(MemoryHTMLBuilder)

        # preload builder module (before init config values)
        if __display_version__ >= "1.6":
            self.preload_builder(buildername)

        # the config file itself can be an extension
        if self.config.setup:
            # py31 doesn't have 'callable' function for below check
            if hasattr(self.config.setup, '__call__'):
                self.config.setup(self)
            else:
                raise ConfigError(
                    _("'setup' as currently defined in conf.py isn't a Python callable. "
                      "Please modify its definition to make it a callable function. This is "
                      "needed for conf.py to behave as a Sphinx extension.")
                )

        verify_required_extensions(self, self.config.needs_extensions)

        # check primary_domain if requested
        primary_domain = self.config.primary_domain
        if __display_version__ >= "1.6":
            if primary_domain and not self.registry.has_domain(primary_domain):
                self.warning(
                    _('primary_domain %r not found, ignored.'), primary_domain)

        # create the builder
        if __display_version__ >= "1.6":
            self.builder = self.create_builder(buildername)
            # check all configuration values for permissible types
            self.config.check_types()
        else:
            self.config.check_types(self.warn)

        # set up source_parsers
        self._init_source_parsers()
        # set up the build environment
        if freshenv:
            self._init_env(freshenv)
        else:
            for domain in self.registry.create_domains(self.env):
                self.env.domains[domain.name] = domain

        if not isinstance(self.env, _CustomBuildEnvironment):
            raise TypeError(
                "self.env is not _CustomBuildEnvironment: '{0}'".format(type(self.env)))

        # set up the builder
        if __display_version__ >= "1.6":
            self._init_builder()
        else:
            self._init_builder(self.buildername)

        # set up the enumerable nodes
        self._init_enumerable_nodes()

        # addition
        self.domains = {}
        self._events = {}

        # now that we know all config values, collect them from conf.py
        # if __display_version__ >= "1.6":
        #     self.config.init_values()
        # else:
        #     self.config.init_values(self.warn)

    def finalize(self, doctree):
        """
        Finalize the documentation after it was parsed.

        @param      doctree     doctree (or pub.document), available after publication
        """
        if not isinstance(self.env, _CustomBuildEnvironment):
            raise TypeError(
                "self.env is not _CustomBuildEnvironment: '{0}'".format(type(self.env)))
        if not isinstance(self.builder.env, _CustomBuildEnvironment):
            raise TypeError("self.builder.env is not _CustomBuildEnvironment: '{0}'".format(
                type(self.builder.env)))
        self.doctree_ = doctree
        self.builder.doctree_ = doctree
        self.env.doctree_[self.config.master_doc] = doctree
        self.env.all_docs = {self.config.master_doc: self.config.master_doc}
        self.emit('doctree-read', doctree)
        self.emit('doctree-resolved', doctree, 'contents')
        self.builder.write(None, None, 'all')

    def debug(self, message, *args, **kwargs):
        pass

    def warn(self, message, location=None, prefix=None,
             type=None, subtype=None, colorfunc=None):
        pass

    def info(self, message='', nonl=False):
        pass

    def warning(self, message='', nonl=False, name=None, type=None, subtype=None):
        pass

    def add_builder(self, builder):
        self._added_objects.append(('builder', builder))
        if self.sphinx__display_version__ >= "1.6":
            if builder.name not in self.registry.builders:
                self.debug('[app] adding builder: %r', builder)
                self.registry.add_builder(builder)
            else:
                self.debug('[app] already added builder: %r', builder)
        else:
            if builder.name not in self.builderclasses:
                Sphinx.add_builder(self, builder)

    def setup_extension(self, extname):
        self._added_objects.append(('extension', extname))
        if self.sphinx__display_version__ >= "1.6":
            self.debug('[app] setting up extension: %r', extname)
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", category=DeprecationWarning)
                    self.registry.load_extension(self, extname)
            except Exception as e:
                raise Exception(
                    "Unable to setup extension '{0}'".format(extname)) from e
        else:
            Sphinx.setup_extension(self, extname)

    def add_directive(self, name, obj, content=None, arguments=None, **options):
        self._added_objects.append(('directive', name))
        if self.sphinx__display_version__ >= "1.6":
            self.debug('[app] adding directive: %r',
                       (name, obj, content, arguments, options))
            if name in directives._directives:
                self.warning(_('while setting up extension %s: directive %r is '
                               'already registered, it will be overridden'),
                             self._setting_up_extension[-1], name,
                             type='app', subtype='add_directive')
            directive = directive_helper(obj, content, arguments, **options)
            directives.register_directive(name, directive)
        else:
            Sphinx.add_directive(
                self, name, obj, content=None, arguments=None, **options)

    def add_domain(self, domain):
        self._added_objects.append(('domain', domain))
        Sphinx.add_domain(self, domain)
        # For some reason, the directives are missing from the main catalog
        # in docutils.
        for k, v in domain.directives.items():
            self.add_directive("{0}:{1}".format(domain.name, k), v)
        for k, v in domain.roles.items():
            self.add_role("{0}:{1}".format(domain.name, k), v)

    def override_domain(self, domain):
        self._added_objects.append(('domain-over', domain))
        Sphinx.override_domain(self, domain)

    def add_role(self, name, role):
        self._added_objects.append(('role', name))
        if self.sphinx__display_version__ >= "1.6":
            self.debug('[app] adding role: %r', (name, role))
            if name in roles._roles:
                self.warning(_('while setting up extension %s: role %r is '
                               'already registered, it will be overridden'),
                             self._setting_up_extension[-1], name,
                             type='app', subtype='add_role')
            roles.register_local_role(name, role)
        else:
            Sphinx.add_role(self, name, role)

    def add_generic_role(self, name, nodeclass):
        self._added_objects.append(('generic_role', name))
        if self.sphinx__display_version__ >= "1.6":
            self.debug('[app] adding generic role: %r', (name, nodeclass))
            if name in roles._roles:
                self.warning(_('while setting up extension %s: role %r is '
                               'already registered, it will be overridden'),
                             self._setting_up_extension[-1], name,
                             type='app', subtype='add_generic_role')
            role = roles.GenericRole(name, nodeclass)
            roles.register_local_role(name, role)
        else:
            Sphinx.add_generic_role(self, name, nodeclass)

    def add_node(self, node, **kwds):
        self._added_objects.append(('node', node))
        if self.sphinx__display_version__ >= "1.6":
            self.debug('[app] adding node: %r', (node, kwds))
            if not kwds.pop('override', False) and \
               hasattr(nodes.GenericNodeVisitor, 'visit_' + node.__name__):
                self.warning(_('while setting up extension %s: node class %r is '
                               'already registered, its visitors will be overridden'),
                             self._setting_up_extension, node.__name__,
                             type='app', subtype='add_node')
            nodes._add_node_class_names([node.__name__])
            for key, val in kwds.items():
                try:
                    visit, depart = val
                except ValueError:
                    raise ExtensionError(_('Value for key %r must be a '
                                           '(visit, depart) function tuple') % key)
                translator = self.registry.translators.get(key)
                translators = []
                if translator is not None:
                    translators.append(translator)
                elif key == 'html':
                    from sphinx.writers.html import HTMLTranslator
                    translators.append(HTMLTranslator)
                    if is_html5_writer_available():
                        from sphinx.writers.html5 import HTML5Translator
                        translators.append(HTML5Translator)
                elif key == 'latex':
                    from sphinx.writers.latex import LaTeXTranslator
                    translators.append(LaTeXTranslator)
                elif key == 'text':
                    from sphinx.writers.text import TextTranslator
                    translators.append(TextTranslator)
                elif key == 'man':
                    from sphinx.writers.manpage import ManualPageTranslator
                    translators.append(ManualPageTranslator)
                elif key == 'texinfo':
                    from sphinx.writers.texinfo import TexinfoTranslator
                    translators.append(TexinfoTranslator)

                for translator in translators:
                    setattr(translator, 'visit_' + node.__name__, visit)
                    if depart:
                        setattr(translator, 'depart_' + node.__name__, depart)
        else:
            Sphinx.add_node(self, node, **kwds)

    def add_event(self, name):
        self._added_objects.append(('event', name))
        Sphinx.add_event(self, name)

    def add_config_value(self, name, default, rebuild, types=()):
        self._added_objects.append(('config_value', name))
        Sphinx.add_config_value(self, name, default, rebuild, types)

    def add_directive_to_domain(self, domain, name, obj,
                                has_content=None, argument_spec=None, **option_spec):
        self._added_objects.append(('directive_to_domain', domain, name))
        Sphinx.add_directive_to_domain(self, domain, name, obj,
                                       has_content=has_content, argument_spec=argument_spec,
                                       **option_spec)

    def add_role_to_domain(self, domain, name, role):
        self._added_objects.append(('roles_to_domain', domain, name))
        Sphinx.add_role_to_domain(self, domain, name, role)

    def add_transform(self, transform):
        self._added_objects.append(('transform', transform))
        Sphinx.add_transform(self, transform)

    def add_post_transform(self, transform):
        self._added_objects.append(('post_transform', transform))
        Sphinx.add_post_transform(self, transform)

    def add_javascript(self, filename):
        self._added_objects.append(('js', filename))
        Sphinx.add_javascript(self, filename)

    def add_stylesheet(self, filename, alternate=False, title=None):
        self._added_objects.append(('css', filename))
        Sphinx.add_stylesheet(self, filename)

    def add_latex_package(self, packagename, options=None):
        self._added_objects.append(('latex', packagename))
        Sphinx.add_latex_package(self, packagename)

    def add_object_type(self, directivename, rolename, indextemplate='',
                        parse_node=None, ref_nodeclass=None, objname='',
                        doc_field_types=[]):
        self._added_objects.append(('object', directivename, rolename))
        Sphinx.add_object_type(self, directivename, rolename, indextemplate=indextemplate,
                               parse_node=parse_node, ref_nodeclass=ref_nodeclass,
                               objname=objname, doc_field_types=doc_field_types)