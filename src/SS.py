import streamlit as st
from itertools import repeat
from inspect import stack
from time import time as now
from Cope import isiterable
import pickle
from warning import warn
warn('This file should no longer be called!')
# THIS IS DEPRICATED. UPDATES SHOULD GO TO COPE.SS INSTEAD

# TODO add auto-page config options
# TODO fix query params between switching pages
# TODO _get_query_params only evaluates the first the first level of the container
class SS:
    """ A better streamlit.session_state interface.
        This class is accessable via it's only instance, `ss`. Do not instantiate this class directly.
        You can use `ss` as a drop-in replacement for st.session_state, and it will work.
        Features:
            - Variables are specified once with defaults, and can be reset and maintained across pages
                via the reset() and maintain_state() methods, respectively. You can use square brackets or
                the . operator to access and set variables, and it won't throw an error if it doesn't already
                exist, instead it will return None.
            - *_changed (named {varname}_changed) gets updated automatically
                when the value gets set. The *_changed variable will not get reset upon the script rerunning
                though, unless you call reset_changed() at the end of the script. It will also not detect
                if the value was changed by widgets. To check if any variables were changed at *all*,
                use the check_changed() method.
                Note that *_changed doesn't ever get reset to False, unless a variable is manually set
                to the same value it already has. To reset all the variables, call ss.reset_changed().
                This is usually done at the end of a file and/or before any st.rerun() calls.
            - `current_page` and `page_changed` variables store the filepath of the
                page we're currently in, and if the page was just changed, respectively.
                In order for the pages to work, you have to call either , update(), maintain_state() or
                note_page() at the top of each page in your project that you want variables to be maintained in.
            - maintain_state() will keep all the variables the same across pages. If arguements are
                passed, it only maintains those. kwargs passed sets the given variables to those values.
            - The `just_loaded` variable gets set to `True` only if it's the first time the page is loaded.
                All other times it's set to `False`. Resetting the page counts as loading the page for
                "the first time".
            - Variables you want to keep track of via query parameters (so they get preserved between
                page reloads, or for sharing URLs with people), you can do that by either specifying
                names of the variables positionally to setup(), or by calling the add_query() method.
                The setup() and add_query() methods will automatically load them on page startup, or
                you can load them yourself on first run using `just_loaded`.
        Current Limitations:
            - Query params will not stay maintained across pages, if the varibles change between
                pages.
            - Using containers with query params behaves oddly sometimes. You may have to parse them
                yourself using eval().
            - TODO: auto-setting the page config on all pages
    """

    maintain = True
    _dict = {}
    _query = set()

    def __init__(self):
        """ The constructor. Not to be called by you. Stop it."""
        st.session_state['ss'] = self
        st.session_state['just_loaded'] = True
        self.ensure_exist()

    def __setitem__(self, name:str, value):
        """ Handles setting the value, the {var}_changes, and the _prev_{var} variables """
        if name not in st.session_state:
            st.session_state[name] = value
        st.session_state[name + '_changed'] = st.session_state[name] != value
        st.session_state['_prev_' + name] = st.session_state[name]
        st.session_state[name] = value
        # If it's a variable we handle with query params
        if name in self._query:
            self._set_query_param(name, value)

    def __setattr__(self, name:str, value):
        """ Shadows __setitem__() """
        self.__setitem__(name, value)

    def __getitem__(self, name:str):
        """ Handles getting variables from either session_state or query parameters """
        queried = None
        session = None

        if name in self._query and name in st.query_params:
            queried = self._get_query_param(name)

        if name in st.session_state:
            session = st.session_state[name]

        # If we have both, we want to overwrite the query parameter with the session value.
        # This is because:
        # 1. First run variables are handled by add_query(), which takes all the values in the query
        # parameters and adds them to the session state immediately
        # 2. session state values may be edited by widgets without SS knowing. This ensures
        # the query parameters remain up to date
        # If we have a value in the session, and somehow don't have a query parameter, and we should,
        # then add it
        if session is not None and name in self._query:
            self._set_query_param(name, session)
            return session
        # If we have a query parameter, and it's somehow not in the session_state, add it
        elif session is None and queried is not None:
            st.session_state[name] = queried
            return queried

        # return session or queried
        return queried or session

    def __getattr__(self, name:str):
        """ shadows __getitem__() """
        return self.__getitem__(name)

    def __delitem__(self, name:str):
        if name in self._dict:
            del self._dict[name]
        del st.session_state[name]

    def __delattr__(self, name:str):
        self.__delitem__(name)

    def __contains__(self, name:str):
        return name in st.session_state


    def _set_query_param(self, name, to):
        """ Handles how we serialize the _query params """
        if isinstance(to, dict):
            to = {repr(key): repr(val) for key, val in to.items()}
        elif isinstance(to, (list, tuple, set)):
            to = type(to)([repr(i) for i in to])
        st.query_params[name] = repr(to)

    def _get_query_param(self, name):
        """ Handles how we deserialize the query params
            TODO: this only evaluates the first level of containers
        """
        return eval(st.query_params[name])

    def setup(self, *queries, **vars):
        """ Pass default values of all the variables you're using.

            If a variable is provided via positional args, and not keyword args, this sets it to be watched
            by query parameters as well.
        """
        assert not len(set(queries) - set(vars.keys())), 'A query variable set isnt in the variables given with default values'
        self._dict.update(vars)
        self.add_query(*queries)
        self.ensure_exist()

    def ensure_exist(self):
        """ Ensures that all the variables we're keeping track of exist in st.session_state, at least
            with default values. This can be, but shouldn't need to be called by the user
        """
        for var, val in self._dict.items():
            if var not in st.session_state:
                st.session_state[var] = val
            if var in self._query and var not in st.query_params:
                self._set_query_param(var, st.session_state[var])
            if var + '_changed' not in st.session_state:
                st.session_state[var + '_changed'] = True
            if '_prev_' + var not in st.session_state:
                st.session_state['_prev_' + var] = None

    def update(self, file):
        """ Maintain variable states across files, and notes the page we're in """
        self.note_page(file)
        if self.maintain:
            self.maintain_state()

    def check_changed(self):
        """ Checks if any variables have been changed by widgets, and if so, updates their associated
            *_changed variable.
            """
        for var in self._dict.keys():
            if var not in st.session_state:
                st.session_state[var] = self._dict[var]
            if '_prev_' + var not in st.session_state:
                st.session_state['_prev_' + var] = None

            st.session_state[var + '_changed'] = st.session_state[var] != st.session_state['_prev_' + var]
            st.session_state['_prev_' + var] = st.session_state[var]

    def maintain_state(self, *args, exclude=[], calls=1, **kwargs):
        """ Maintain the current variables with the values they currently have across pages """
        if len(args):
            for var in args:
                # Add the new var, if it's new
                if var not in self._dict:
                    raise ValueError("Variable specified not already being watched. To add it, please use keyword arguments to specify a default.")
                else:
                    st.session_state[var] = st.session_state[var]
        else:
            for var, val in self._dict.items():
                if var in exclude:
                    continue
                elif var not in st.session_state:
                    st.session_state[var] = val
                else:
                    st.session_state[var] = st.session_state[var]
        for var, val in kwargs.items():
            # Add the new var, if it's new
            if var not in self._dict:
                self._dict[var] = val
            st.session_state[var] = val

    def note_page(self, file, calls=1):
        """ Manually take note of what page we're running from """
        self.check_changed()

        # This causes some very strange loop thing
        # file = st_javascript("await fetch('').then(r => window.parent.location.href)", key=now())

        # This will *only* work in pages directly, not functions in other files
        # This doesn't work, because the streamlit stack is what calls these things
        # file = stack()[-calls].filename

        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = file

        # A quick alias cause they both make sense
        st.session_state['current_page_changed'] = st.session_state['page_changed'] = \
            st.session_state['current_page'] != file
        st.session_state['current_page'] = file

    def reset(self):
        """ Reset all variables to their defaults """
        for var, val in self._dict.items():
            # The *_changed should stay accurate
            if var in st.session_state:
                st.session_state[var + '_changed'] = st.session_state[var] != val
            else:
                st.session_state[var + '_changed'] = True
            # So prev reinitializes
            # st.session_state[var] = val
            self[var] = val

    def reset_changed(self):
        """ Sets all the *_changed variables to False """
        for var in self._dict.keys():
            st.session_state[var + '_changed'] = False
        st.session_state['just_loaded'] = False

    def get(self, name):
        """ Available just for compatibility """
        return self[name]

    def watch(self, name:str, default):
        """ Sets a single variable to be maintained and guarenteed to exist in st.session_state """
        self._dict[name] = default

    def add_query(self, *names):
        """ Adds variables to be monitored with query parameters as well. Names must already be set
            to be watched. This should only realistically be called once, in the main file.
        """
        for name in names:
            if name not in self._dict:
                raise ValueError(f"{name} not previously set to be watched, please provide a default.")
            else:
                self._query.add(name)
            # If a query param is given (i.e. on first run via bookmark), we want to use *that* value
            # and *not* the default.
            # But we want it to *only* run once, the first time the page loads. Otherwise, we'll be
            # resetting values set the previous run by widgets, which we don't want.
            # This shouldn't be necissary?...
            if 'just_loaded' not in st.session_state:
                st.session_state['just_loaded'] = True

            if st.session_state['just_loaded']:
                for name in st.query_params.to_dict().keys():
                    st.session_state[name] = self._get_query_param(name)

ss = SS()
