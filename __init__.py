try:
    # Note the relative import!
    from .action_swap_pins import SwapPins
    # Instantiate and register to Pcbnew
    SwapPins().register()
# if failed, log the error and let the user know
except Exception as e:
    # log the error
    import os
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'swap_pins_error.log')
    with open(log_file, 'w') as f:
        f.write(repr(e))
    # register dummy plugin, to let the user know of the problems
    import pcbnew
    import wx

    class SwapPins(pcbnew.ActionPlugin):
        """
        Notify user of error
        """

        def defaults(self):
            self.name = "Swap Pins"
            self.category = "Dummy"
            self.description = "Dummy plugin for minimal user feedback"

        def Run(self):
            caption = self.name
            message = "There was an error while loading plugin \n" \
                      "Please take a look in the plugin folder for swap_pins_error.log\n" \
                      "You can raise an issue on GitHub page.\n" \
                      "Please attach the .log file"
            dlg = wx.MessageBox(message, caption, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    SwapPins().register()

