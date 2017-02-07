#
from os import system
import resources.sickpotatohead as sickpotatohead
import xbmc

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "https://github.com/lsellens/service.downloadmanager.SickPotatoHead"

# Launch programs
sickpotatohead.main()

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    
    while not monitor.abortRequested():
        if monitor.waitForAbort():
            # Shutdown SickPotatoHead
            system("kill `ps | grep -E 'python.*service.downloadmanager.SickPotatoHead' | awk '{print $1}'`")
            break
