# Initializes and launches Couchpotato V2, Sickbeard and Headphones
from xml.dom.minidom import parseString
from lib.configobj import ConfigObj
import os
import subprocess
import hashlib
import xbmc
import xbmcaddon
import xbmcvfs

# helper functions
# ----------------


def create_dir(dirname):
    if not xbmcvfs.exists(dirname):
        xbmcvfs.mkdirs(dirname)
        xbmc.log('SickPotatoHead: Created directory ' + dirname, level=xbmc.LOGDEBUG)
# define some things that we're gonna need, mainly paths
# ------------------------------------------------------

# addon
__addon__             = xbmcaddon.Addon(id='service.downloadmanager.SickPotatoHead')
__addonpath__         = xbmc.translatePath(__addon__.getAddonInfo('path'))
__addonhome__         = xbmc.translatePath(__addon__.getAddonInfo('profile'))

# settings
pDefaultSuiteSettings = xbmc.translatePath(__addonpath__ + '/settings-default.xml')
pSuiteSettings        = xbmc.translatePath(__addonhome__ + 'settings.xml')
pXbmcSettings         = xbmc.translatePath('special://home/userdata/guisettings.xml')
pSickBeardSettings    = xbmc.translatePath(__addonhome__ + 'sickbeard.ini')
pCouchPotatoServerSettings  = xbmc.translatePath(__addonhome__ + 'couchpotatoserver.ini')
pHeadphonesSettings   = xbmc.translatePath(__addonhome__ + 'headphones.ini')

# create the settings file if missing
if not xbmcvfs.exists(pSuiteSettings):
    xbmcvfs.copy(pDefaultSuiteSettings, pSuiteSettings)

#Get Device Home DIR
pHomeDIR = os.path.expanduser('~/')

# directories
pSickPotatoHeadComplete       = pHomeDIR+'downloads'
pSickPotatoHeadCompleteTV     = pHomeDIR+'downloads/tvshows'
pSickPotatoHeadCompleteMov    = pHomeDIR+'downloads/movies'
pSickPotatoHeadWatchDir       = pHomeDIR+'downloads/watch'

# pylib
pPylib                = xbmc.translatePath(__addonpath__ + '/resources/lib')

# service commands
sickBeard             = ['python', xbmc.translatePath(__addonpath__ + '/resources/SickBeard/SickBeard.py'),
                         '--daemon', '--datadir', __addonhome__,'--pidfile=/run/sickbeard.pid', '--config', pSickBeardSettings]
couchPotatoServer     = ['python', xbmc.translatePath(__addonpath__ + '/resources/CouchPotatoServer/CouchPotato.py'),
                         '--daemon', '--pid_file', xbmc.translatePath(__addonhome__ + 'couchpotato.pid'),
                         '--config_file', pCouchPotatoServerSettings]
headphones            = ['python', xbmc.translatePath(__addonpath__ + '/resources/Headphones/Headphones.py'),
                         '-d', '--datadir', __addonhome__, '--config', pHeadphonesSettings]

# create directories and settings if missing
# -----------------------------------------------

sbfirstLaunch = not xbmcvfs.exists(pSickBeardSettings)
cpfirstLaunch = not xbmcvfs.exists(pCouchPotatoServerSettings)
hpfirstLaunch = not xbmcvfs.exists(pHeadphonesSettings)

xbmc.log('SickPotatoHead: Creating directories if missing', level=xbmc.LOGDEBUG)
create_dir(__addonhome__)
create_dir(pSickPotatoHeadComplete)
create_dir(pSickPotatoHeadCompleteTV)
create_dir(pSickPotatoHeadCompleteMov)
create_dir(pSickPotatoHeadWatchDir)

# read addon and xbmc settings
# ----------------------------

# Transmission-Daemon
transauth = False
try:
   transmissionaddon = xbmcaddon.Addon(id='service.downloadmanager.transmission')
   transauth = (transmissionaddon.getSetting('TRANSMISSION_AUTH').lower() == 'true')

   if transauth:
        xbmc.log('SickPotatoHead: Transmission Authentication Enabled', level=xbmc.LOGDEBUG)
        transuser = (transmissionaddon.getSetting('TRANSMISSION_USER').decode('utf-8'))
        if transuser == '':
            transuser = None
        transpwd = (transmissionaddon.getSetting('TRANSMISSION_PWD').decode('utf-8'))
        if transpwd == '':
            transpwd = None
    else:
        xbmc.log('SickPotatoHead: Transmission Authentication Not Enabled', level=xbmc.LOGDEBUG)

except Exception, e:
    xbmc.log('SickPotatoHead: Transmission Settings are not present', level=xbmc.LOGNOTICE)
    xbmc.log(str(e), level=xbmc.LOGNOTICE)
    pass

# SickPotatoHead-Suite
user = (__addon__.getSetting('SICKPOTATOHEAD_USER').decode('utf-8'))
pwd = (__addon__.getSetting('SICKPOTATOHEAD_PWD').decode('utf-8'))
host = (__addon__.getSetting('SICKPOTATOHEAD_IP'))
sickbeard_launch = (__addon__.getSetting('SICKBEARD_LAUNCH').lower() == 'true')
couchpotato_launch = (__addon__.getSetting('COUCHPOTATO_LAUNCH').lower() == 'true')
headphones_launch = (__addon__.getSetting('HEADPHONES_LAUNCH').lower() == 'true')

# XBMC
fXbmcSettings                 = open(pXbmcSettings, 'r')
data                          = fXbmcSettings.read()
fXbmcSettings.close()
xbmcSettings                  = parseString(data)
xbmcServices                  = xbmcSettings.getElementsByTagName('services')[0]
xbmcPort                      = xbmcServices.getElementsByTagName('webserverport')[0].firstChild.data
try:
    xbmcUser                      = xbmcServices.getElementsByTagName('webserverusername')[0].firstChild.data
except StandardError:
    xbmcUser                      = ''
try:
    xbmcPwd                       = xbmcServices.getElementsByTagName('webserverpassword')[0].firstChild.data
except StandardError:
    xbmcPwd                       = ''

# prepare execution environment
# -----------------------------
parch                         = os.uname()[4]

xbmc.log('SickPotatoHead: ' + parch + ' architecture detected', level=xbmc.LOGDEBUG)

if not xbmcvfs.exists(xbmc.translatePath(pPylib + '/arch.' + parch)):
    xbmc.log('SickPotatoHead: Setting up binaries:', level=xbmc.LOGDEBUG)

    if xbmcvfs.exists(xbmc.translatePath(pPylib + '/arch.i686')):
        xbmcvfs.delete(xbmc.translatePath(pPylib + '/arch.i686'))
    if xbmcvfs.exists(xbmc.translatePath(pPylib + '/arch.x86_64')):
        xbmcvfs.delete(xbmc.translatePath(pPylib + '/arch.x86_64'))
    if xbmcvfs.exists(xbmc.translatePath(pPylib + '/arch.armv6l')):
        xbmcvfs.delete(xbmc.translatePath(pPylib + '/arch.armv6l'))
    if xbmcvfs.exists(xbmc.translatePath(pPylib + '/arch.armv7l')):
        xbmcvfs.delete(xbmc.translatePath(pPylib + '/arch.armv7l'))

    pnamemapper                   = xbmc.translatePath(pPylib + '/Cheetah/_namemapper.so')
    punrar                        = xbmc.translatePath(__addonpath__ + '/bin/unrar')

    try:
        fnamemapper                   = xbmc.translatePath(pPylib + '/multiarch/_namemapper.so.' + parch)
        xbmcvfs.copy(fnamemapper, pnamemapper)
        xbmc.log('SickPotatoHead: Copied _namemapper.so for ' + parch, level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('SickPotatoHead: Error Copying _namemapper.so for ' + parch, level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)

    try:
        funrar                        = xbmc.translatePath(pPylib + '/multiarch/unrar.' + parch)
        xbmcvfs.copy(funrar, punrar)
        os.chmod(punrar, 0755)
        xbmc.log('SickPotatoHead: Copied unrar for ' + parch, level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('SickPotatoHead: Error Copying unrar for ' + parch, level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)

    xbmcvfs.File(xbmc.translatePath(pPylib + '/arch.' + parch), 'w').close()

os.environ['PYTHONPATH'] = str(os.environ.get('PYTHONPATH')) + ':' + pPylib

# SickBeard start
try:
    # write SickBeard settings
    # ------------------------
    sickBeardConfig = ConfigObj(pSickBeardSettings, create_empty=True)
    defaultConfig = ConfigObj()
    defaultConfig['General'] = {}
    defaultConfig['General']['launch_browser']      = '0'
    defaultConfig['General']['version_notify']      = '0'
    defaultConfig['General']['web_port']            = '8082'
    defaultConfig['General']['web_host']            = host
    defaultConfig['General']['web_username']        = user
    defaultConfig['General']['web_password']        = pwd
    defaultConfig['General']['cache_dir']           = __addonhome__ + 'sbcache'
    defaultConfig['General']['log_dir']             = __addonhome__ + 'logs'
    defaultConfig['XBMC'] = {}
    defaultConfig['XBMC']['use_xbmc']               = '1'
    defaultConfig['XBMC']['xbmc_host']              = 'localhost:' + xbmcPort
    defaultConfig['XBMC']['xbmc_username']          = xbmcUser
    defaultConfig['XBMC']['xbmc_password']          = xbmcPwd
    defaultConfig['TORRENT'] = {}

    if transauth:
        defaultConfig['TORRENT']['torrent_username']         = transuser
        defaultConfig['TORRENT']['torrent_password']         = transpwd
        defaultConfig['TORRENT']['torrent_host']             = 'http://localhost:9091/'

    if sbfirstLaunch:
        defaultConfig['TORRENT']['torrent_path']          = pSickPotatoHeadCompleteTV
        defaultConfig['General']['tv_download_dir']       = pSickPotatoHeadComplete
        defaultConfig['General']['metadata_xbmc_12plus']  = '0|0|0|0|0|0|0|0|0|0'
        defaultConfig['General']['keep_processed_dir']    = '0'
        defaultConfig['General']['use_banner']            = '1'
        defaultConfig['General']['rename_episodes']       = '1'
        defaultConfig['General']['naming_ep_name']        = '0'
        defaultConfig['General']['naming_use_periods']    = '1'
        defaultConfig['General']['naming_sep_type']       = '1'
        defaultConfig['General']['naming_ep_type']        = '1'
        defaultConfig['General']['root_dirs']             = '0|'+pHomeDIR+'tvshows'
        defaultConfig['General']['naming_custom_abd']     = '0'
        defaultConfig['General']['naming_abd_pattern']    = '%SN - %A-D - %EN'
        defaultConfig['Blackhole'] = {}
        defaultConfig['Blackhole']['torrent_dir']         = pSickPotatoHeadWatchDir
        defaultConfig['EZRSS'] = {}
        defaultConfig['EZRSS']['ezrss']                   = '1'
        defaultConfig['PUBLICHD'] = {}
        defaultConfig['PUBLICHD']['publichd']             = '1'
        defaultConfig['KAT'] = {}
        defaultConfig['KAT']['kat']                       = '1'
        defaultConfig['THEPIRATEBAY'] = {}
        defaultConfig['THEPIRATEBAY']['thepiratebay']     = '1'
        defaultConfig['Womble'] = {}
        defaultConfig['Womble']['womble']                 = '0'
        defaultConfig['XBMC']['xbmc_notify_ondownload']   = '1'
        defaultConfig['XBMC']['xbmc_notify_onsnatch']     = '1'
        defaultConfig['XBMC']['xbmc_update_library']      = '1'
        defaultConfig['XBMC']['xbmc_update_full']         = '1'

    sickBeardConfig.merge(defaultConfig)
    sickBeardConfig.write()

    # launch SickBeard
    # ----------------
    if sickbeard_launch:
        xbmc.log('SickPotatoHead: Launching SickBeard...', level=xbmc.LOGDEBUG)
        subprocess.call(sickBeard, close_fds=True)
        xbmc.log('SickPotatoHead: ...done', level=xbmc.LOGDEBUG)
except Exception, e:
    xbmc.log('SickPotatoHead: SickBeard exception occurred', level=xbmc.LOGERROR)
    xbmc.log(str(e), level=xbmc.LOGERROR)
# SickBeard end

# CouchPotatoServer start
try:
    # empty password hack
    if pwd == '':
        md5pwd = ''
    else:
        #convert password to md5
        md5pwd = hashlib.md5(str(pwd)).hexdigest()

    # write CouchPotatoServer settings
    # --------------------------
    couchPotatoServerConfig = ConfigObj(pCouchPotatoServerSettings, create_empty=True, list_values=False)
    defaultConfig = ConfigObj()
    defaultConfig['core'] = {}
    defaultConfig['core']['username']               = user
    defaultConfig['core']['password']               = md5pwd
    defaultConfig['core']['port']                   = '8083'
    defaultConfig['core']['launch_browser']         = '0'
    defaultConfig['core']['host']                   = host
    defaultConfig['core']['data_dir']               = __addonhome__
    defaultConfig['updater'] = {}
    defaultConfig['updater']['enabled']             = '0'
    defaultConfig['updater']['notification']        = '0'
    defaultConfig['updater']['automatic']           = '0'
    defaultConfig['xbmc'] = {}
    defaultConfig['xbmc']['enabled']                = '1'
    defaultConfig['xbmc']['host']                   = 'localhost:' + xbmcPort
    defaultConfig['xbmc']['username']               = xbmcUser
    defaultConfig['xbmc']['password']               = xbmcPwd
    defaultConfig['transmission'] = {}

    if transauth:
        defaultConfig['transmission']['username']         = transuser
        defaultConfig['transmission']['password']         = transpwd
        defaultConfig['transmission']['host']             = 'localhost:9091'

    if cpfirstLaunch:
        defaultConfig['transmission']['directory']        = pSickPotatoHeadCompleteMov
        defaultConfig['xbmc']['xbmc_update_library']      = '1'
        defaultConfig['xbmc']['xbmc_update_full']         = '1'
        defaultConfig['xbmc']['xbmc_notify_onsnatch']     = '1'
        defaultConfig['xbmc']['xbmc_notify_ondownload']   = '1'
        defaultConfig['blackhole'] = {}
        defaultConfig['blackhole']['directory']           = pSickPotatoHeadWatchDir
        defaultConfig['blackhole']['use_for']             = 'torrent'
        defaultConfig['blackhole']['enabled']             = '0'
        defaultConfig['renamer'] = {}
        defaultConfig['renamer']['enabled']               = '0'
        defaultConfig['renamer']['from']                  = pSickPotatoHeadCompleteMov
        defaultConfig['renamer']['separator']             = '.'
        defaultConfig['renamer']['cleanup']               = '0'
        defaultConfig['nzbindex'] = {}
        defaultConfig['nzbindex']['enabled']              = '0'
        defaultConfig['mysterbin'] = {}
        defaultConfig['mysterbin']['enabled']             = '0'
        defaultConfig['core']['permission_folder']        = '0644'
        defaultConfig['core']['permission_file']          = '0644'
        defaultConfig['core']['show_wizard']            = '0'
        defaultConfig['core']['debug']                  = '0'
        defaultConfig['core']['development']            = '0'
        defaultConfig['searcher'] = {}
        defaultConfig['searcher']['preferred_method']     = 'torrent'

    couchPotatoServerConfig.merge(defaultConfig)
    couchPotatoServerConfig.write()

    # launch CouchPotatoServer
    # ------------------
    if couchpotato_launch:
        xbmc.log('SickPotatoHead: Launching CouchPotatoServer...', level=xbmc.LOGDEBUG)
        subprocess.call(couchPotatoServer, close_fds=True)
        xbmc.log('SickPotatoHead: ...done', level=xbmc.LOGDEBUG)
except Exception, e:
    xbmc.log('SickPotatoHead: CouchPotatoServer exception occurred', level=xbmc.LOGERROR)
    xbmc.log(str(e), level=xbmc.LOGERROR)
# CouchPotatoServer end

# Headphones start
try:
    # write Headphones settings
    # -------------------------
    headphonesConfig = ConfigObj(pHeadphonesSettings, create_empty=True)
    defaultConfig = ConfigObj()
    defaultConfig['General'] = {}
    defaultConfig['General']['launch_browser']            = '0'
    defaultConfig['General']['http_port']                 = '8084'
    defaultConfig['General']['http_host']                 = host
    defaultConfig['General']['http_username']             = user
    defaultConfig['General']['http_password']             = pwd
    defaultConfig['General']['check_github']              = '0'
    defaultConfig['General']['check_github_on_startup']   = '0'
    defaultConfig['General']['cache_dir']                 = __addonhome__ + 'hpcache'
    defaultConfig['General']['log_dir']                   = __addonhome__ + 'logs'
    defaultConfig['XBMC'] = {}
    defaultConfig['XBMC']['xbmc_enabled']                 = '1'
    defaultConfig['XBMC']['xbmc_host']                    = 'localhost:' + xbmcPort
    defaultConfig['XBMC']['xbmc_username']                = xbmcUser
    defaultConfig['XBMC']['xbmc_password']                = xbmcPwd
    defaultConfig['Transmission'] = {}

    if transauth:
        defaultConfig['Transmission']['transmission_username'] = transuser
        defaultConfig['Transmission']['transmission_password'] = transpwd
        defaultConfig['Transmission']['transmission_host']     = 'http://localhost:9091'

    if hpfirstLaunch:
        defaultConfig['XBMC']['xbmc_update']                  = '1'
        defaultConfig['XBMC']['xbmc_notify']                  = '1'
        defaultConfig['General']['music_dir']                 = pHomeDIR+'music'
        defaultConfig['General']['destination_dir']           = pHomeDIR+'music'
        defaultConfig['General']['torrentblackhole_dir']      = pSickPotatoHeadWatchDir
        defaultConfig['General']['download_torrent_dir']      = pSickPotatoHeadComplete
        defaultConfig['General']['move_files']                = '1'
        defaultConfig['General']['rename_files']              = '1'
        defaultConfig['General']['folder_permissions']        = '0644'
        defaultConfig['General']['isohunt']                   = '1'
        defaultConfig['General']['kat']                       = '1'
        defaultConfig['General']['mininova']                  = '1'
        defaultConfig['General']['piratebay']                 = '1'

    headphonesConfig.merge(defaultConfig)
    headphonesConfig.write()

    # launch Headphones
    # -----------------
    if headphones_launch:
        xbmc.log('SickPotatoHead: Launching Headphones...', level=xbmc.LOGDEBUG)
        subprocess.call(headphones, close_fds=True)
        xbmc.log('SickPotatoHead: ...done', level=xbmc.LOGDEBUG)
except Exception, e:
    xbmc.log('SickPotatoHead: Headphones exception occurred', level=xbmc.LOGERROR)
    xbmc.log(str(e), level=xbmc.LOGERROR)
# Headphones end
