import streamlit as st
from itertools import repeat
from inspect import currentframe


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
            - `current_page` and `page_changed` variables store the filepath of the
                page we're currently in, and if the page was just changed, respectively.
                In order for the pages to work, you have to call either maintain_state() or note_page()
                at the top of each page in your project.
            - maintain_state() will keep all the variables the same across pages. If arguements are
                passed, it only maintains those. kwargs passed sets the given variables to those values.
    """
    auto_init = True
    default_default = None

    def __init__(self, *args, init=True, **kwargs):
        """ Pass default values of all the variables you're using
            If a variable is provided, a default default value is set using the `default_default`
            parameter.
        """
        self._vars = kwargs
        self._vars.update(dict(zip(args, repeat(default_default))))

        # Psuedonymn
        self.init = self.reset
        if auto_init or init:
            self.reset()
        self.reset_changed()

        file = currentframe().f_back.f_code.co_filename
        print(file)
        st.session_state['current_page_changed'] = st.session_state['page_changed'] = False
        st.session_state['current_page'] = file

        st.session_state['ss'] = self

    def __setitem__(self, key:str, value):
        st.session_state[name + '_changed'] = st.session_state[name] != value
        st.session_state[name] = name

    def __setattr__(self, name:str, value):
        self.__setitem__(name, value)

    def __getitem__(self, key:str):
        if name in st.session_state:
            return st.session_state[name]

    def __getattr__(self, name:str):
        return self.__getitem__(name)

    def __contains__(self, item:str):
        return item in st.session_state

    def maintain_state(self, *args, exclude=[], **kwargs):
        """ Maintain the current variables with the values they currently have across pages"""
        self.note_page()
        if len(args):
            for var in args:
                # Add the new var, if it's new
                if var not in self._vars:
                    self._vars[var] = self.default_default
                    st.session_state[var] = self.default_default
                else:
                    st.session_state[var] = st.session_state[var]
        else:
            for var, val in self._vars.items():
                if var in exclude:
                    continue
                elif var not in st.session_state:
                    st.session_state[var] = val
                else:
                    st.session_state[var] = st.session_state[var]
        for var, val in kwargs.items():
            # Add the new var, if it's new
            if var not in self._vars:
                self._vars[var] = val
            st.session_state[var] = val

    def note_page(self):
        file = currentframe().f_back.f_code.co_filename
        # A quick alias cause they both make sense
        st.session_state['current_page_changed'] = st.session_state['page_changed'] = \
            st.session_state['current_page'] != file
        st.session_state['current_page'] = file

    def reset(self):
        """ Reset all variables to their defaults """
        self.note_page()
        for var, val in self._vars.items():
            if var in st.session_state:
                st.session_state[var + '_changed'] = st.session_state[var] != val
            else:
                st.session_state[var + '_changed'] = True
            st.session_state[var] = val

    def reset_changed(self):
        self.note_page()
        for var in self._vars.keys():
            st.session_state[var + '_changed'] = False
