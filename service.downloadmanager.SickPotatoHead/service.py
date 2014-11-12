#
import xbmc
import xbmcaddon
import time

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "http://code.google.com/p/repository-lsellens/"
__addon__      = xbmcaddon.Addon(id='service.downloadmanager.SickPotatoHead')
__addonpath__  = __addon__.getAddonInfo('path')
__start__      = xbmc.translatePath(__addonpath__ + '/resources/SickPotatoHead.py')
__stop__       = xbmc.translatePath(__addonpath__ + '/resources/SickPotatoHead.stop.py')

xbmc.executebuiltin('XBMC.RunScript(%s)' % __start__, True)

while not xbmc.abortRequested:
    time.sleep(0.250)

xbmc.executebuiltin('XBMC.RunScript(%s)' % __stop__, True)
