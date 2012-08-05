"""
Main GUI window for stars
"""

__author__ = 'Serge Rey <sjsrey@gmail.com'
__all__ = ['guiMain']

APPNAME = "Space-Time Analysis of Regional Systems: STARS 0.9dev"


import sys
PLATFORM = sys.platform
import wx
print PLATFORM


ID_PROJECT_CLOSE = 1



class AppWindow(wx.Frame):
    """
    Main Application Window
    
    """
    def __init__(self, parent, **kwargs):
        size = (480, 84) # set these dynamically by query window size
        position = (100,100)
    
        wx.Frame.__init__(self, parent, -1, APPNAME, pos=position,
                size=size)
        self.do_menus()

    def do_menus(self):

        # file menu

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New Project")
        file_menu.Append(wx.ID_OPEN, "&Open Project")
        file_menu.Append(wx.ID_SAVE, '&Save Project')
        file_menu.Append(ID_PROJECT_CLOSE, '&Close Project')
        file_menu.AppendSeparator()

        imp = wx.Menu()
        imp.Append(wx.ID_ANY, 'Import Shapefile...')
        imp.Append(wx.ID_ANY, 'Import Attribute Data...')
        imp.Append(wx.ID_ANY, 'Import Weights...')
        file_menu.AppendMenu(wx.ID_ANY, '&Import', imp)
        file_menu.AppendSeparator()
        quitItem = file_menu.Append(wx.ID_EXIT, '&Quit STARS')


        # data menu
        data_menu = wx.Menu()
        data_menu.Append(wx.ID_ANY, "Data")

        # weights menu
        weights_menu = wx.Menu()
        weights_menu.Append(wx.ID_ANY, "Weights")


        # analysis menu
        analysis_menu = wx.Menu()
        analysis_menu.Append(wx.ID_ANY, "Analysis")


        # visualization menu
        visualization_menu = wx.Menu()
        visualization_menu.Append(wx.ID_ANY, "Visualization")



        # help menu

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, 'About')

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, 'File')
        menu_bar.Append(data_menu, 'Data')
        menu_bar.Append(weights_menu, 'Weights')
        menu_bar.Append(analysis_menu, 'Analysis')
        menu_bar.Append(visualization_menu, 'Visualization')
        menu_bar.Append(help_menu, 'Help')
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)

    def OnQuit(self, e):
        self.Close()



def guiMain():
    app = wx.App()
    main = AppWindow(None)
    main.Show()
    app.MainLoop()

if __name__ == '__main__':
    guiMain()



