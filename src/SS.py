import streamlit as st
from itertools import repeat
from inspect import stack
# from streamlit_javascript import st_javascript
from time import time as now
from Cope import isiterable

# TODO add more documentation
# TODO add auto-page config options
# TODO add query params
class SS:
    """ A better streamlit.session_state interface.
        There should only be 1 instance of this class, preferably in the main streamlit file. The
        instance of this class is accessable at st.session_state.ss, after it's be initialized.
        Features:
            - Variables are specified once with defaults, and can be reset and maintained across pages
                via the reset() and maintain_state() methods, respectively. You can use square brackets or
                the . operator to access and set variables, and it won't throw an error if it doesn't already
                exist.
            - *_changed (named {varname}_changed) gets updated automatically
                when the value gets set. The *_changed variable will not get reset upon the script rerunning
                though, unless you call reset_changed() at the end of the script.
            - `current_page` and `page_changed` variables store the name of the file of the
                page we're currently in, and if the page was just changed, respectively.
                In order for the pages to work, you have to call either maintain_state() or note_page()
                at the top of each page in your project.
            - maintain_state() will keep all the variables the same across pages. If arguements are
                passed, it only maintains those. kwargs passed sets the given variables to those values.
    """
    default_default = None
    maintain = True
    dict = {}
    query = set()

    def __init__(self):
        st.session_state['ss'] = self
        self.ensure_exist()

    def __setitem__(self, name:str, value):
        if name not in st.session_state:
            st.session_state[name] = value
        st.session_state[name + '_changed'] = st.session_state[name] != value
        st.session_state['_prev_' + name] = st.session_state[name]
        st.session_state[name] = value
        # If it's a variable we handle with query params
        # TODO: handle lists and iterables and such
        if name in self.query:
            if isiterable(value, include_str=False):
                raise NotImplementedError('At the moment, containers are not supported via query parameters')
                # st.query_params[name] = str(value)
            else:
                st.query_params[name] = value

    def __setattr__(self, name:str, value):
        self.__setitem__(name, value)

    def __getitem__(self, name:str):
        queried = None
        session = None

        if name in self.query and name in st.query_params:
            queried = st.query_params[name]

        if name in st.session_state:
            session = st.session_state[name]

        if name == '_expr' or name == 'vars_dict':
            print(f'getting {name}: query has {queried}, session has {session}')

        # If we have both, we want to overwrite the query parameter with the session value.
        # This is because:
        # 1. First run variables are handled by add_query(), which takes all the values in the query
        # parameters and adds them to the session state immediately
        # 2. session state values may be edited by widgets without SS knowing. This ensures
        # the query parameters remain up to date
        # If we have a value in the session, and somehow don't have a query parameter, and we should,
        # then add it
        if session is not None and name in self.query:
            st.query_params[name] = session
            return session
        # If we have a query parameter, and it's somehow not in the session_state, add it
        elif session is None and queried is not None:
            print('this shouldnt be running')
            st.session_state[name] = queried
            return queried

        # return session or queried
        return queried or session

    def __getattr__(self, name:str):
        return self.__getitem__(name)

    def __delitem__(self, name:str):
        if name in self.dict:
            del self.dict[name]
        del st.session_state[name]

    def __delattr__(self, name:str):
        self.__delitem__(name)

    def __contains__(self, name:str):
        return name in st.session_state


    def setup(self, *queries, **vars):
        """ Pass default values of all the variables you're using.
            If a variable is provided via args, and not given a default value, this sets it to be watched
            by query parameters as well.
        """
        assert not len(set(queries) - set(vars.keys())), 'A query variable set isnt in the variables given with default values'
        self.dict.update(vars)
        # {a: self.default_default for a in args}
        # self.dict.update(dict(zip(args, repeat(self.default_default))))
        self.add_query(*queries)
        self.ensure_exist()

    def ensure_exist(self):
        for var, val in self.dict.items():
            if var not in st.session_state:
                st.session_state[var] = val
            if var in self.query and var not in st.query_params:
                st.query_params[var] = st.session_state[var]
            if var + '_changed' not in st.session_state:
                st.session_state[var + '_changed'] = True
            if '_prev_' + var not in st.session_state:
                st.session_state['_prev_' + var] = None

    def update(self, file):
        self.note_page(file)
        if self.maintain:
            self.maintain_state()

    def check_changed(self):
        for var in self.dict.keys():
            if var not in st.session_state:
                st.session_state[var] = self.dict[var]
            if '_prev_' + var not in st.session_state:
                st.session_state['_prev_' + var] = None

            st.session_state[var + '_changed'] = st.session_state[var] != st.session_state['_prev_' + var]
            st.session_state['_prev_' + var] = st.session_state[var]

    def maintain_state(self, *args, exclude=[], calls=1, **kwargs):
        """ Maintain the current variables with the values they currently have across pages """
        if len(args):
            for var in args:
                # Add the new var, if it's new
                if var not in self.dict:
                    self.dict[var] = self.default_default
                    st.session_state[var] = self.default_default
                else:
                    st.session_state[var] = st.session_state[var]
        else:
            for var, val in self.dict.items():
                if var in exclude:
                    continue
                elif var not in st.session_state:
                    st.session_state[var] = val
                else:
                    st.session_state[var] = st.session_state[var]
        for var, val in kwargs.items():
            # Add the new var, if it's new
            if var not in self.dict:
                self.dict[var] = val
            st.session_state[var] = val

    def note_page(self, file, calls=1):
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
        for var, val in self.dict.items():
            # The *_changed should stay accurate
            if var in st.session_state:
                st.session_state[var + '_changed'] = st.session_state[var] != val
            else:
                st.session_state[var + '_changed'] = True
            # So prev reinitializes
            # st.session_state[var] = val
            self[var] = val

    def init(self):
        """ Reset all variables to their defaults """
        for var, val in self.dict.items():
            # Initialize the *_changed
            st.session_state[var + '_changed'] = True
            # Initialze the _prev_*
            st.session_state['_prev_' + var] = None
            # Initialze the variables
            st.session_state[var] = val

    def reset_changed(self):
        for var in self.__dict__.keys():
            st.session_state[var + '_changed'] = False

    def get(self, name):
        """ Available just for compatibility """
        return self[name]

    def watch(self, name, default=...):
        self.__dict__[name] = default if defaults is not Ellipsis else self.default_default

    def add_query(self, *names):
        """ Adds variables to be monitored with query parameters as well. Names must already be set
            to be watched. This should only realistically be called once, in the main file.
        """
        for name in names:
            if name not in self.dict:
                raise ValueError(f"{name} not previously set to be watched, please provide a default.")
            else:
                self.query.add(name)
            # If a query param is given (i.e. on first run via bookmark), we want to use *that* value
            # and *not* the default.
            # if name in st.query_params:
                # self[name] = st.query_params[name]

ss = SS()
