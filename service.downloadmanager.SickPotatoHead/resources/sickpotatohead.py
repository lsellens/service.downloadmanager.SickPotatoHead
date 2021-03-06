# Initializes and launches Couchpotato V2, Sickbeard and Headphones
from lib.configobj import ConfigObj
import json
import os
import subprocess
import hashlib
import xbmc
import xbmcaddon
import xbmcvfs


def main():
    # helper functions
    def create_dir(dirname):
        if not xbmcvfs.exists(dirname):
            xbmcvfs.mkdirs(dirname)
            xbmc.log('SickPotatoHead: Created directory ' + dirname, level=xbmc.LOGDEBUG)
    
    
    def jsonrpc(method, *args):
        values = {"jsonrpc": "2.0", "id": "1", "method": method}
        if args:
            values["params"] = args
        json_cmd = json.dumps(values, sort_keys=True, separators=(',', ':'))
        json_cmd = json_cmd.replace('[{', '{')
        json_cmd = json_cmd.replace('}]', '}')
        return json_cmd
    
    
    # define some things that we're gonna need, mainly paths
    # ------------------------------------------------------
    
    # addon
    __addon__             = xbmcaddon.Addon(id='service.downloadmanager.SickPotatoHead')
    __addonpath__         = xbmc.translatePath(__addon__.getAddonInfo('path'))
    __addonhome__         = xbmc.translatePath(__addon__.getAddonInfo('profile'))
    
    # settings
    pdefaultsuitesettings = xbmc.translatePath(__addonpath__ + '/settings-default.xml')
    psuitesettings        = xbmc.translatePath(__addonhome__ + 'settings.xml')
    psickbeardsettings    = xbmc.translatePath(__addonhome__ + 'sickbeard.ini')
    pcouchpotatoserversettings  = xbmc.translatePath(__addonhome__ + 'couchpotatoserver.ini')
    pheadphonessettings   = xbmc.translatePath(__addonhome__ + 'headphones.ini')
    
    # create the settings file if missing
    if not xbmcvfs.exists(psuitesettings):
        xbmcvfs.copy(pdefaultsuitesettings, psuitesettings)
    
    # Get Device Home DIR
    phomedir = os.path.expanduser('~/')
    
    # directories
    psickpotatoheadcomplete    = phomedir + 'downloads'
    psickpotatoheadcompletetv  = phomedir + 'downloads/tvshows'
    psickpotatoheadcompletemov = phomedir + 'downloads/movies'
    psickpotatoheadwatchdir    = phomedir + 'downloads/watch'
    
    # pylib
    ppylib            = xbmc.translatePath(__addonpath__ + '/resources/lib')
    
    # service commands
    sickbeard         = ['python', xbmc.translatePath(__addonpath__ + '/resources/SickBeard/SickBeard.py'),
                         '--daemon', '--datadir', __addonhome__, '--pidfile=/var/run/sickbeard.pid', '--config',
                         psickbeardsettings]
    couchpotatoserver = ['python', xbmc.translatePath(__addonpath__ + '/resources/CouchPotatoServer/CouchPotato.py'),
                         '--daemon', '--pid_file=/var/run/couchpotato.pid', '--config_file', pcouchpotatoserversettings]
    headphones        = ['python', xbmc.translatePath(__addonpath__ + '/resources/Headphones/Headphones.py'),
                         '-d', '--datadir', __addonhome__, '--pidfile=/var/run/headphones.pid', '--config',
                         pheadphonessettings]
    
    # create directories and settings if missing
    # -----------------------------------------------
    
    sbfirstlaunch = not xbmcvfs.exists(psickbeardsettings)
    cpfirstlaunch = not xbmcvfs.exists(pcouchpotatoserversettings)
    hpfirstlaunch = not xbmcvfs.exists(pheadphonessettings)
    
    xbmc.log('SickPotatoHead: Creating directories if missing', level=xbmc.LOGDEBUG)
    create_dir(__addonhome__)
    create_dir(psickpotatoheadcomplete)
    create_dir(psickpotatoheadcompletetv)
    create_dir(psickpotatoheadcompletemov)
    create_dir(psickpotatoheadwatchdir)
    
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
    parameters = {'setting': 'services.webserverport'}
    xbmcport = json.loads(xbmc.executeJSONRPC(jsonrpc('Settings.GetSettingValue', parameters)))
    parameters = {'setting': 'services.webserverusername'}
    xbmcuser = json.loads(xbmc.executeJSONRPC(jsonrpc('Settings.GetSettingValue', parameters)))
    parameters = {'setting': 'services.webserverpassword'}
    xbmcpwd = json.loads(xbmc.executeJSONRPC(jsonrpc('Settings.GetSettingValue', parameters)))
    
    # prepare execution environment
    # -----------------------------
    parch                         = os.uname()[4]
    
    xbmc.log('SickPotatoHead: ' + parch + ' architecture detected', level=xbmc.LOGDEBUG)
    
    if not xbmcvfs.exists(xbmc.translatePath(ppylib + '/arch.' + parch)):
        xbmc.log('SickPotatoHead: Setting up binaries:', level=xbmc.LOGDEBUG)
    
        if xbmcvfs.exists(xbmc.translatePath(ppylib + '/arch.x86_64')):
            xbmcvfs.delete(xbmc.translatePath(ppylib + '/arch.x86_64'))
        if xbmcvfs.exists(xbmc.translatePath(ppylib + '/arch.armv6l')):
            xbmcvfs.delete(xbmc.translatePath(ppylib + '/arch.armv6l'))
        if xbmcvfs.exists(xbmc.translatePath(ppylib + '/arch.armv7l')):
            xbmcvfs.delete(xbmc.translatePath(ppylib + '/arch.armv7l'))
        pobjectify       = xbmc.translatePath(__addonpath__ + '/resources/lib/lxml/objectify.so')
        petree           = xbmc.translatePath(__addonpath__ + '/resources/lib/lxml/etree.so')
        p_constant_time  = xbmc.translatePath(__addonpath__ + '/resources/lib/cryptography/hazmat/bindings/_constant_time.so')
        p_openssl        = xbmc.translatePath(__addonpath__ + '/resources/lib/cryptography/hazmat/bindings/_openssl.so')
        p_padding        = xbmc.translatePath(__addonpath__ + '/resources/lib/cryptography/hazmat/bindings/_padding.so')
        plibcrypto       = xbmc.translatePath(__addonpath__ + '/resources/lib/OpenSSL/libcrypto.so.1.0.0')
        plibssl          = xbmc.translatePath(__addonpath__ + '/resources/lib/OpenSSL/libssl.so.1.0.0')
        plibcryptolk     = xbmc.translatePath(__addonpath__ + '/resources/lib/libcrypto.so.1.0.0')
        plibssllk        = xbmc.translatePath(__addonpath__ + '/resources/lib/libssl.so.1.0.0')
        plibffi          = xbmc.translatePath(__addonpath__ + '/resources/lib/libffi.so.6.0.4')
        plibffilk        = xbmc.translatePath(__addonpath__ + '/resources/lib/libffi.so.6')
        p_cffi_backend   = xbmc.translatePath(__addonpath__ + '/resources/lib/_cffi_backend.so')
        punrar           = xbmc.translatePath(__addonpath__ + '/bin/unrar')
        
        try:
            if xbmcvfs.exists(pobjectify):
                xbmcvfs.delete(pobjectify)
            fobjectify = xbmc.translatePath(ppylib + '/multiarch/objectify.so.' + parch)
            xbmcvfs.copy(fobjectify, pobjectify)
            os.chmod(pobjectify, 0755)
            xbmc.log('SickPotatoHead: Copied objectify.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying objectify.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(petree):
                xbmcvfs.delete(petree)
            fetree = xbmc.translatePath(ppylib + '/multiarch/etree.so.' + parch)
            xbmcvfs.copy(fetree, petree)
            os.chmod(petree, 0755)
            xbmc.log('SickPotatoHead: Copied etree.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying etree.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(p_constant_time):
                xbmcvfs.delete(p_constant_time)
            f_constant_time = xbmc.translatePath(ppylib + '/multiarch/_constant_time.so.' + parch)
            xbmcvfs.copy(f_constant_time, p_constant_time)
            os.chmod(p_constant_time, 0755)
            xbmc.log('SickPotatoHead: Copied _constant_time.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying _constant_time.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(p_openssl):
                xbmcvfs.delete(p_openssl)
            f_openssl = xbmc.translatePath(ppylib + '/multiarch/_openssl.so.' + parch)
            xbmcvfs.copy(f_openssl, p_openssl)
            os.chmod(p_openssl, 0755)
            xbmc.log('SickPotatoHead: Copied _openssl.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying _openssl.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(p_padding):
                xbmcvfs.delete(p_padding)
            f_padding = xbmc.translatePath(ppylib + '/multiarch/_padding.so.' + parch)
            xbmcvfs.copy(f_padding, p_padding)
            os.chmod(p_padding, 0755)
            xbmc.log('SickPotatoHead: Copied _padding.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying _padding.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(plibcrypto):
                xbmcvfs.delete(plibcrypto)
            flibcrypto = xbmc.translatePath(ppylib + '/multiarch/libcrypto.so.1.0.0.' + parch)
            xbmcvfs.copy(flibcrypto, plibcrypto)
            os.chmod(plibcrypto, 0755)
            os.symlink(plibcrypto, plibcryptolk)
            xbmc.log('SickPotatoHead: Copied libcrypto for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying libcrypto for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(plibssl):
                xbmcvfs.delete(plibssl)
            flibssl = xbmc.translatePath(ppylib + '/multiarch/libssl.so.1.0.0.' + parch)
            xbmcvfs.copy(flibssl, plibssl)
            os.chmod(plibssl, 0755)
            os.symlink(plibssl, plibssllk)
            xbmc.log('SickPotatoHead: Copied libssl for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying libssl for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(plibffi):
                xbmcvfs.delete(plibffi)
            flibffi = xbmc.translatePath(ppylib + '/multiarch/libffi.so.6.0.4.' + parch)
            xbmcvfs.copy(flibffi, plibffi)
            os.chmod(plibffi, 0755)
            os.symlink(plibffi, plibffilk)
            xbmc.log('SickPotatoHead: Copied libffi for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying libffi for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(p_cffi_backend):
                xbmcvfs.delete(p_cffi_backend)
            f_cffi_backend = xbmc.translatePath(ppylib + '/multiarch/_cffi_backend.so.' + parch)
            xbmcvfs.copy(f_cffi_backend, p_cffi_backend)
            os.chmod(p_cffi_backend, 0755)
            xbmc.log('SickPotatoHead: Copied _cffi_backend.so for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying _cffi_backend.so for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        try:
            if xbmcvfs.exists(punrar):
                xbmcvfs.delete(punrar)
            funrar = xbmc.translatePath(ppylib + '/multiarch/unrar.' + parch)
            xbmcvfs.copy(funrar, punrar)
            os.chmod(punrar, 0755)
            xbmc.log('SickPotatoHead: Copied unrar for ' + parch, level=xbmc.LOGDEBUG)
        except Exception, e:
            xbmc.log('SickPotatoHead: Error Copying unrar for ' + parch, level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
        
        xbmcvfs.File(xbmc.translatePath(ppylib + '/arch.' + parch), 'w').close()
    
    os.environ['PYTHONPATH'] = str(os.environ.get('PYTHONPATH')) + ':' + ppylib
    os.environ['LD_LIBRARY_PATH'] = str(os.environ.get('LD_LIBRARY_PATH')) + ':' + ppylib
    os.environ['PYTHONPATH'] = str(os.environ.get('PYTHONPATH')) + ':' + (xbmc.translatePath(__addonpath__ + '/bin'))
    
    # SickBeard start
    try:
        # write SickBeard settings
        # ------------------------
        sickbeardconfig = ConfigObj(psickbeardsettings, create_empty=True)
        defaultconfig = ConfigObj()
        defaultconfig['General'] = {}
        defaultconfig['General']['launch_browser']             = '0'
        defaultconfig['General']['version_notify']             = '0'
        defaultconfig['General']['web_port']                   = '8082'
        defaultconfig['General']['web_host']                   = host
        defaultconfig['General']['web_username']               = user
        defaultconfig['General']['web_password']               = pwd
        defaultconfig['General']['cache_dir']                  = __addonhome__ + 'sbcache'
        defaultconfig['General']['log_dir']                    = __addonhome__ + 'logs'
        defaultconfig['KODI'] = {}
        defaultconfig['KODI']['use_kodi']                      = '1'
        defaultconfig['KODI']['kodi_host']                     = 'localhost:' + str(xbmcport['result']['value'])
        defaultconfig['KODI']['kodi_username']                 = xbmcuser['result']['value']
        defaultconfig['KODI']['kodi_password']                 = xbmcpwd['result']['value']
        defaultconfig['TORRENT'] = {}
    
        if transauth:
            defaultconfig['TORRENT']['torrent_username']           = transuser
            defaultconfig['TORRENT']['torrent_password']           = transpwd
            defaultconfig['TORRENT']['torrent_host']               = 'http://localhost:9091/'
    
        if sbfirstlaunch:
            defaultconfig['TORRENT']['torrent_path']               = psickpotatoheadcompletetv
            defaultconfig['General']['tv_download_dir']            = psickpotatoheadcomplete
            defaultconfig['General']['metadata_kodi_12plus']       = '0|0|0|0|0|0|0|0|0|0'
            defaultconfig['General']['keep_processed_dir']         = '0'
            defaultconfig['General']['use_banner']                 = '1'
            defaultconfig['General']['rename_episodes']            = '1'
            defaultconfig['General']['naming_ep_name']             = '0'
            defaultconfig['General']['naming_use_periods']         = '1'
            defaultconfig['General']['naming_sep_type']            = '1'
            defaultconfig['General']['naming_ep_type']             = '1'
            defaultconfig['General']['root_dirs']                  = '0|' + phomedir + 'tvshows'
            defaultconfig['General']['naming_custom_abd']          = '0'
            defaultconfig['General']['naming_abd_pattern']         = '%SN - %A-D - %EN'
            defaultconfig['Blackhole'] = {}
            defaultconfig['Blackhole']['torrent_dir']              = psickpotatoheadwatchdir
            defaultconfig['EZRSS'] = {}
            defaultconfig['EZRSS']['ezrss']                        = '1'
            defaultconfig['PUBLICHD'] = {}
            defaultconfig['PUBLICHD']['publichd']                  = '1'
            defaultconfig['KAT'] = {}
            defaultconfig['KAT']['kat']                            = '1'
            defaultconfig['THEPIRATEBAY'] = {}
            defaultconfig['THEPIRATEBAY']['thepiratebay']          = '1'
            defaultconfig['Womble'] = {}
            defaultconfig['Womble']['womble']                      = '0'
            defaultconfig['KODI']['kodi_notify_ondownload']        = '1'
            defaultconfig['KODI']['kodi_notify_onsnatch']          = '1'
            defaultconfig['KODI']['kodi_update_library']           = '1'
            defaultconfig['KODI']['kodi_update_full']              = '1'
    
        sickbeardconfig.merge(defaultconfig)
        sickbeardconfig.write()
    
        # launch SickBeard
        # ----------------
        if sickbeard_launch:
            xbmc.log('SickPotatoHead: Launching SickBeard...', level=xbmc.LOGDEBUG)
            if os.path.isfile("/var/run/sickbeard.pid"):
                os.system("kill `cat /var/run/sickbeard.pid`")
            subprocess.call(sickbeard, close_fds=True)
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
            # convert password to md5
            md5pwd = hashlib.md5(str(pwd)).hexdigest()
    
        # write CouchPotatoServer settings
        # --------------------------
        couchpotatoserverconfig = ConfigObj(pcouchpotatoserversettings, create_empty=True, list_values=False)
        defaultconfig = ConfigObj()
        defaultconfig['core'] = {}
        defaultconfig['core']['username']                      = user
        defaultconfig['core']['password']                      = md5pwd
        defaultconfig['core']['port']                          = '8083'
        defaultconfig['core']['launch_browser']                = '0'
        defaultconfig['core']['host']                          = host
        defaultconfig['core']['data_dir']                      = __addonhome__
        defaultconfig['updater'] = {}
        defaultconfig['updater']['enabled']                    = '0'
        defaultconfig['updater']['notification']               = '0'
        defaultconfig['updater']['automatic']                  = '0'
        defaultconfig['xbmc'] = {}
        defaultconfig['xbmc']['enabled']                       = '1'
        defaultconfig['xbmc']['host']                          = 'localhost:' + str(xbmcport['result']['value'])
        defaultconfig['xbmc']['username']                      = xbmcuser['result']['value']
        defaultconfig['xbmc']['password']                      = xbmcpwd['result']['value']
        defaultconfig['transmission'] = {}
    
        if transauth:
            defaultconfig['transmission']['username']              = transuser
            defaultconfig['transmission']['password']              = transpwd
            defaultconfig['transmission']['host']                  = 'localhost:9091'
    
        if cpfirstlaunch:
            defaultconfig['transmission']['directory']             = psickpotatoheadcompletemov
            defaultconfig['xbmc']['xbmc_update_library']           = '1'
            defaultconfig['xbmc']['xbmc_update_full']              = '1'
            defaultconfig['xbmc']['xbmc_notify_onsnatch']          = '1'
            defaultconfig['xbmc']['xbmc_notify_ondownload']        = '1'
            defaultconfig['blackhole'] = {}
            defaultconfig['blackhole']['directory']                = psickpotatoheadwatchdir
            defaultconfig['blackhole']['use_for']                  = 'torrent'
            defaultconfig['blackhole']['enabled']                  = '0'
            defaultconfig['renamer'] = {}
            defaultconfig['renamer']['enabled']                    = '0'
            defaultconfig['renamer']['from']                       = psickpotatoheadcompletemov
            defaultconfig['renamer']['separator']                  = '.'
            defaultconfig['renamer']['cleanup']                    = '0'
            defaultconfig['nzbindex'] = {}
            defaultconfig['nzbindex']['enabled']                   = '0'
            defaultconfig['mysterbin'] = {}
            defaultconfig['mysterbin']['enabled']                  = '0'
            defaultconfig['core']['permission_folder']             = '0644'
            defaultconfig['core']['permission_file']               = '0644'
            defaultconfig['core']['show_wizard']                   = '0'
            defaultconfig['core']['debug']                         = '0'
            defaultconfig['core']['development']                   = '0'
            defaultconfig['searcher'] = {}
            defaultconfig['searcher']['preferred_method']          = 'torrent'
    
        couchpotatoserverconfig.merge(defaultconfig)
        couchpotatoserverconfig.write()
    
        # launch CouchPotatoServer
        # ------------------
        if couchpotato_launch:
            xbmc.log('SickPotatoHead: Launching CouchPotatoServer...', level=xbmc.LOGDEBUG)
            if os.path.isfile("/var/run/couchpotato.pid"):
                os.system("kill `cat /var/run/couchpotato.pid`")
            subprocess.call(couchpotatoserver, close_fds=True)
            xbmc.log('SickPotatoHead: ...done', level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('SickPotatoHead: CouchPotatoServer exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
    # CouchPotatoServer end
    
    # Headphones start
    try:
        # write Headphones settings
        # -------------------------
        headphonesconfig = ConfigObj(pheadphonessettings, create_empty=True)
        defaultconfig = ConfigObj()
        defaultconfig['General'] = {}
        defaultconfig['General']['launch_browser']             = '0'
        defaultconfig['General']['http_port']                  = '8084'
        defaultconfig['General']['http_host']                  = host
        defaultconfig['General']['http_username']              = user
        defaultconfig['General']['http_password']              = pwd
        defaultconfig['General']['check_github']               = '0'
        defaultconfig['General']['check_github_on_startup']    = '0'
        defaultconfig['General']['cache_dir']                  = __addonhome__ + 'hpcache'
        defaultconfig['General']['log_dir']                    = __addonhome__ + 'logs'
        defaultconfig['XBMC'] = {}
        defaultconfig['XBMC']['xbmc_enabled']                  = '1'
        defaultconfig['XBMC']['xbmc_host']                     = 'localhost:' + str(xbmcport['result']['value'])
        defaultconfig['XBMC']['xbmc_username']                 = xbmcuser['result']['value']
        defaultconfig['XBMC']['xbmc_password']                 = xbmcpwd['result']['value']
        defaultconfig['Transmission'] = {}
    
        if transauth:
            defaultconfig['Transmission']['transmission_username'] = transuser
            defaultconfig['Transmission']['transmission_password'] = transpwd
            defaultconfig['Transmission']['transmission_host']     = 'http://localhost:9091'
    
        if hpfirstlaunch:
            defaultconfig['XBMC']['xbmc_update']                   = '1'
            defaultconfig['XBMC']['xbmc_notify']                   = '1'
            defaultconfig['General']['music_dir']                  = phomedir + 'music'
            defaultconfig['General']['destination_dir']            = phomedir + 'music'
            defaultconfig['General']['torrentblackhole_dir']       = psickpotatoheadwatchdir
            defaultconfig['General']['download_torrent_dir']       = psickpotatoheadcomplete
            defaultconfig['General']['move_files']                 = '1'
            defaultconfig['General']['rename_files']               = '1'
            defaultconfig['General']['folder_permissions']         = '0644'
            defaultconfig['General']['isohunt']                    = '1'
            defaultconfig['General']['kat']                        = '1'
            defaultconfig['General']['mininova']                   = '1'
            defaultconfig['General']['piratebay']                  = '1'
    
        headphonesconfig.merge(defaultconfig)
        headphonesconfig.write()
    
        # launch Headphones
        # -----------------
        if headphones_launch:
            xbmc.log('SickPotatoHead: Launching Headphones...', level=xbmc.LOGDEBUG)
            if os.path.isfile("/var/run/headphones.pid"):
                os.system("kill `cat /var/run/headphones.pid`")
            subprocess.call(headphones, close_fds=True)
            xbmc.log('SickPotatoHead: ...done', level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log('SickPotatoHead: Headphones exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
    # Headphones end
