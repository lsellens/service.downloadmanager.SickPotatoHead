#
from os import system
import resources.sickpotatohead as sickpotatohead
import xbmc

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "https://github.com/lsellens/service.downloadmanager.SickPotatoHead"

# Launch programs
sickpotatohead.main()

while not xbmc.abortRequested:
    xbmc.sleep(250)

# Shutdown SickPotatoHead
system("kill `ps | grep -E 'python.*service.downloadmanager.SickPotatoHead' | awk '{print $1}'`")
