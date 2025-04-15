
try:
    # Note the relative import!
    from .action_swap_stubs import SwapStubs
    # Instantiate and register to Pcbnew
    SwapStubs().register()
# if failed, log the error and let the user know
except Exception as e:
    # log the error
    import os
    import time
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'swap_stubs_error.log')
    with open(log_file, 'w') as f:
        #f.write(str(time.clock()))
        f.write(repr(e))
    # register dummy plugin, to let the user know of the problems
    import pcbnew
    import wx

    class SwapStubs(pcbnew.ActionPlugin):
        """
        Notify user of error
        """

        def defaults(self):
            self.name = "Swap Stubs"
            self.category = "Dummy"
            self.description = "Dummy plugin for minimal user feedback"

        def Run(self):
            caption = self.name
            message = "There was an error while loading plugin \n" \
                      "Please take a look in the plugin folder for swap_stubs_error.log\n" \
                      "You can raise an issue on GitHub page.\n" \
                      "Please attach the .log file"
            dlg = wx.MessageBox(message, caption, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    SwapStubs().register()

