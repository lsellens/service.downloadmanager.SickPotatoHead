#
from os import system
import resources.sickpotatohead as sickpotatohead
import xbmc
import time

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "http://code.google.com/p/repository-lsellens/"

# Launch programs
sickpotatohead.main()

while not xbmc.abortRequested:
    time.sleep(0.250)

# Shutdown SickPotatoHead
system("kill `ps | grep -E 'python.*service.downloadmanager.SickPotatoHead' | awk '{print $1}'`")
