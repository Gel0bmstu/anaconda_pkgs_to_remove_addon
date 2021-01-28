#
# Copyright (C) 2013  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Vratislav Podzimek <vpodzime@redhat.com>
#
#
# NOTE: Anaconda is using Simpleline library for Text User Interface.
#       To learn how to use Simpleline look on the documentation:
#
#       http://python-simpleline.readthedocs.io/en/latest/
#


"""Module with the class for the Hello world TUI spoke."""

import logging
import re

from simpleline.render.screen import InputState
from simpleline.render.containers import ListColumnContainer
from simpleline.render.widgets import CheckboxWidget, EntryWidget, TextWidget

from pyanaconda.ui.tui.spokes import NormalTUISpoke
from pyanaconda.ui.common import FirstbootSpokeMixIn
# Simpleline's dialog configured for use in Anaconda
from pyanaconda.ui.tui.tuiobject import Dialog, PasswordDialog

# the path to addons is in sys.path so we can import things from org_fedora_hello_world
from org_fedora_hello_world.categories.hello_world import HelloWorldCategory
from org_fedora_hello_world.constants import HELLO_WORLD

log = logging.getLogger(__name__)

# export only the HelloWorldSpoke and HelloWorldEditSpoke classes
__all__ = ["HelloWorldSpoke"]

# import gettext
# _ = lambda x: gettext.ldgettext("hello-world-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x


class HelloWorldSpoke(FirstbootSpokeMixIn, NormalTUISpoke):
    """
    Class for the Hello world TUI spoke that is a subclass of NormalTUISpoke. It
    is a simple example of the basic unit for Anaconda's text user interface.
    Since it is also inherited form the FirstbootSpokeMixIn, it will also appear
    in the Initial Setup (successor of the Firstboot tool).

    :see: pyanaconda.ui.tui.TUISpoke
    :see: pyanaconda.ui.common.FirstbootSpokeMixIn
    :see: simpleline.render.widgets.Widget
    """

    ### class attributes defined by API ###

    # category this spoke belongs to
    category = HelloWorldCategory

    def __init__(self, data, storage, payload):
        """
        :see: simpleline.render.screen.UIScreen
        :param data: data object passed to every spoke to load/store data
                     from/to it
        :type data: pykickstart.base.BaseHandler
        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet
        :param payload: object storing packaging-related information
        :type payload: pyanaconda.packaging.Payload
        """
        NormalTUISpoke.__init__(self, data, storage, payload)
        self.title = N_("Package to remove")

        self._hello_world_module = HELLO_WORLD.get_proxy()

        self._remove = []
        self._list = []

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize
        """
        NormalTUISpoke.initialize(self)

    def refresh(self, args=None):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh
        :see: simpleline.render.screen.UIScreen.refresh
        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything
        """
        # call parent method to setup basic container with screen title set
        super().refresh(args)

        pkgs_list = self._hello_world_module.Lines

        self._container = ListColumnContainer(columns=3)
        self.window.add(self._container)

        for pkg in pkgs_list:
            c = CheckboxWidget(title=pkg, completed=(pkg in self._remove))
            self._container.add(c, self._checkbox_called, pkg)

        self._window.add_separator()

    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the spoke.
        """
        self._hello_world_module.SetLines(self._remove)

    def execute(self):
        """
        The execute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the spoke.
        """
        # nothing to do here
        pass

    @property
    def completed(self):
        """
        The completed property that tells whether all mandatory items on the
        spoke are set, or not. The spoke will be marked on the hub as completed
        or uncompleted according to the returned value.

        :rtype: bool
        """
        return True

    @property
    def status(self):
        """
        The status property that is a brief string describing the state of the
        spoke. It should describe whether all values are set and if possible
        also the values themselves. The returned value will appear on the hub
        below the spoke's title.

        :rtype: str
        """
        pkgs_count = len(self._remove)
        if pkgs_count == 0:
            return _('Select packages, that would be removed in installed system')
        else:
            return _('You selected {} packages'.format(pkgs_count))

    def input(self, args, key):
        """
        The input method that is called by the main loop on user's input.

        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything
        :param key: user's input
        :type key: unicode
        :return: if the input should not be handled here, return it, otherwise
                 return InputState.PROCESSED or InputState.DISCARDED if the input was
                 processed successfully or not respectively
        :rtype: enum InputState
        """
        if self._container.process_user_input(key):
            return InputState.PROCESSED_AND_REDRAW
        else:
            return super().input(args=args, key=key)

    def _checkbox_called(self, data):
        if data in self._remove:
            self._remove.remove(data)
        else:
            self._remove.append(data)