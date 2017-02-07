#
import xbmcaddon

__scriptname__ = "SickPotatoHead"
__author__     = "lsellens"
__url__        = "https://github.com/lsellens/service.downloadmanager.SickPotatoHead"
__addon__   = xbmcaddon.Addon(id='service.downloadmanager.SickPotatoHead')

#Open settings dialog
if __name__ == '__main__':
    __addon__.openSettings()
