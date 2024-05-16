from os import system
import resources.sickpotatohead as sickpotatohead
import xbmc

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "https://github.com/lsellens/xbmc.addons"

# Launch programs
sickpotatohead.main()

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        system("kill `ps | grep -E 'python.*service.downloadmanager.SickPotatoHead' | awk '{print $1}'`")
        sickpotatohead.main()


if __name__ == '__main__':
    monitor = MyMonitor()
    
    while not monitor.abortRequested():
        if monitor.waitForAbort():
            # Shutdown SickPotatoHead
            system("kill `ps | grep -E 'python.*service.downloadmanager.SickPotatoHead' | awk '{print $1}'`")
            break

