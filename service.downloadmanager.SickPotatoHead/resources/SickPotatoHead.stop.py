import urllib2
import xbmc
import xbmcaddon
from lib.configobj import ConfigObj

__addon__ = xbmcaddon.Addon(id='service.downloadmanager.SickPotatoHead')
__addonhome__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
sickbeard_launch = (__addon__.getSetting('SICKBEARD_LAUNCH').lower() == 'true')
couchpotato_launch = (__addon__.getSetting('COUCHPOTATO_LAUNCH').lower() == 'true')
headphones_launch = (__addon__.getSetting('HEADPHONES_LAUNCH').lower() == 'true')

if sickbeard_launch:
    try:
        pSickBeardSettings = xbmc.translatePath(__addonhome__ + 'sickbeard.ini')
        sickBeardConfig = ConfigObj(pSickBeardSettings, create_empty=False)
        sickBeardApiKey = sickBeardConfig['General']['api_key']
        urllib2.urlopen('http://localhost:8082/api/' + sickBeardApiKey + '/?cmd=sb.shutdown')
        xbmc.log('AUDO: Shutting SickBeard down...', level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('AUDO: SickBeard exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
        pass

if couchpotato_launch:
    try:
        pCouchPotatoServerSettings = xbmc.translatePath(__addonhome__ + 'couchpotatoserver.ini')
        couchPotatoServerConfig = ConfigObj(pCouchPotatoServerSettings, create_empty=False, list_values=False)
        CouchPotatoApiKey = couchPotatoServerConfig['core']['api_key']
        urllib2.urlopen('http://localhost:8083/api/' + CouchPotatoApiKey + '/app.shutdown')
        xbmc.log('AUDO: Shutting CouchPotato down...', level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('AUDO: CouchPotato exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
        pass

if headphones_launch:
    try:
        pHeadphonesSettings = xbmc.translatePath(__addonhome__ + 'headphones.ini')
        headphonesConfig = ConfigObj(pHeadphonesSettings, create_empty=False)
        headphonesApiKey = headphonesConfig['General']['api_key']
        urllib2.urlopen('http://localhost:8084/api?apikey=' + headphonesApiKey + '&cmd=shutdown')
        xbmc.log('AUDO: Shutting HeadPhones down...', level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('AUDO: HeadPhones exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
        pass