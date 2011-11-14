"""
Utility classes related to file managing for GUI_Lattice_Tuner

:author: Yoshiteru Hidaka
"""

import sys

import os
import time
import cPickle

import PyQt4.Qt as Qt

from knob import KnobGroupList

SENDER_KEY_TUNER = 'TunerGUI'
SENDER_KEY_CONFIG_SETUP = 'ConfigSetupGUI'
SENDER_KEY_CHANNEL_SELECTOR = 'ChannelSelectorGUI'

########################################################################
class TunerFileManager(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        super(TunerFileManager,self).__init__()
        
        self.version = '0.1.0'
        self.fileExt_ConfigFile    = '.cfg'
        self.fileExt_SnapshotFile  = '.snp'
        self.fileExt_TunerPrefFile = '.prf'
        
        self.starting_directory_path = os.getcwd()
        
    
    #----------------------------------------------------------------------
    def _getSenderKey(self):
        """"""
        
        sender_class = str(type(self.sender()))

        if (sender_class.find('TunerApp') != -1) or \
           (sender_class.find('preferencesDialogForTuner') != -1):
            sender_key = SENDER_KEY_TUNER
        elif (sender_class.find('TunerConfigSetupView') != -1) or \
             (sender_class.find('TunerConfigSetupApp') != -1) or \
             (sender_class.find('preferencesDialogForConfigSetup') != -1):
            sender_key = SENDER_KEY_CONFIG_SETUP
        elif sender_class.find('ChannelSelectorAppp') != -1:
            sender_key = SENDER_KEY_CHANNEL_SELECTOR
        else:
            raise Exception, 'Unknown sender class: ' + sender_class
        
        
        return sender_key
        
    #----------------------------------------------------------------------
    def _createPreferencesDict(self,
                               visible_col_name_list):
        """
        """
        
        preferences = {'version':self.version,
                       'time_stamp':time.time()}
        
        pref_properties = {
            'visible_column_name_list':visible_col_name_list}

        preferences[self._getSenderKey()] = pref_properties

        return preferences
    
    #----------------------------------------------------------------------
    def _createConfigDict(self, model):
        """"""
        
        preferences = self._createPreferencesDict(
            model.col_name_list)
        
        tuner_config = {'version':self.version,
                        'time_stamp':time.time(),
                        'name':model.config_name,
                        'data':model.knobGroupList,
                        'preferences':preferences,
                        'config_description':model.config_description}
        
        return tuner_config
        
    #----------------------------------------------------------------------
    def _createSnapshotDict(self, model):
        """"""
        
        tuner_config = self._createConfigDict(model)
        
        snapshot = {'version':self.version,
                    'time_stamp':time.time(),
                    'tuner_config':tuner_config,
                    'flat_knob_list':model.flat_knob_list,
                    'snapshot_read':model.snapshot_read,
                    'snapshot_setp':model.snapshot_setp,
                    'snapshot_read_timestamp':model.snapshot_read_timestamp,
                    'snapshot_setp_timestamp':model.snapshot_setp_timestamp,
                    'snapshot_description':model.snapshot_description}
        
        return snapshot
        
    #----------------------------------------------------------------------
    def saveConfigFile(self, model):
        """"""
        
        #dialog = Qt.QFileDialog()
        #dialog.setFileMode(Qt.QFileDialog.AnyFile)
        #dialog.setNameFilters([('Tuner configuration files (*' + 
                                #self.fileExt_ConfigFile + ')'),
                               #'All files (*)'])
        #dialog.setWindowTitle('Save Tuner Configuration File')
        #dialog.setDirectory(self.starting_directory_path)
        #dialog.setAcceptMode(Qt.QFileDialog.AcceptSave)
                
        #not_cancelled = dialog.exec_()
        
        #if not not_cancelled: # If the dialog was cancelled
            #return

        #fileNames = dialog.selectedFiles()
            
        #filename = str(fileNames[0])
        
        caption = 'Save Tuner Configuration File'
        selected_filter_str = ('Tuner configuration files (*' +
                               self.fileExt_ConfigFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getSaveFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)

        if filename[-len(self.fileExt_ConfigFile):] != \
           self.fileExt_ConfigFile:
            filename = filename + self.fileExt_ConfigFile
                
        self.starting_directory_path = filename
            
        tuner_config = self._createConfigDict(model)
        f = open(filename, 'w')
        cPickle.dump(tuner_config, f)
        f.close()
        
#----------------------------------------------------------------------
    def loadConfigOrSnapshotFileToSetupGUI(self):
        """"""
        
        caption = 'Load Tuner Configuration/Snapshot File'
        selected_filter_str = ('Tuner configuration/snapshot files (*' + 
                               self.fileExt_ConfigFile + ' *' + 
                               self.fileExt_SnapshotFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getOpenFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)

    
        self.starting_directory_path = filename
            
        f = open(filename, 'r')
        try:
            data = cPickle.load(f)
        except ImportError as detail:
            print detail
            return
        except: # catch all other exceptions
            #print sys.exc_info()[0]
            print 'Unpickling the file failed. ' + \
                  'You probably did not select a ' + \
                  'pickled file.'
            return
        finally:
            f.close()

        if type(data) != dict:
            print 'ERROR: Loaded data object is not a dict.'
            return
            
        if not data.has_key('version'):
            print 'ERROR: Loaded dict must have the key "version".'
            return
     
        if data['version'] == '0.1.0':
            
            if data.has_key('tuner_config'):
                tuner_config = data['tuner_config']
            else:
                tuner_config = data
                
            knobGroupList = tuner_config['data']
            
            if not knobGroupList:
                return
            
            self.emit(Qt.SIGNAL('knobGroupListLoaded'),
                      knobGroupList)
            
            #config_data = self._extractConfigData(tuner_config)
            
            #if not config_data:
                #return
            
            #self.emit(Qt.SIGNAL('configDataLoaded'), config_data)
        else:
            print 'Loading of a tuner configuration/snapshot file ' + \
                  'with version ' + data.version + \
                  'is not supported.'


    #----------------------------------------------------------------------
    def loadConfigFile(self, model_to_be_replaced):
        """"""
        
        caption = 'Load Tuner Configuration File'
        selected_filter_str = ('Tuner configuration files (*' + 
                               self.fileExt_ConfigFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getOpenFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)
        
        
        self.starting_directory_path = filename
            
        f = open(filename, 'r')
        try:
            tuner_config = cPickle.load(f)
        except: # catch all exceptions
            print 'Unpickling the file failed. ' + \
                  'You probably did not select a ' + \
                  'pickled file.'
            return
        finally:
            f.close()
            
        if type(tuner_config) != dict:
            print 'ERROR: Loaded data object is not a dict.'
            return
            
        if not tuner_config.has_key('version'):
            print 'ERROR: Loaded dict must have the key "version".'
            return
     
        if tuner_config['version'] == '0.1.0':
            
            config_data = self._extractConfigData(tuner_config)
            
            if not config_data:
                return
            
            self.emit(Qt.SIGNAL('configFileLoaded'), 
                      model_to_be_replaced, config_data)
        else:
            print 'Loading of a tuner configuration file ' + \
                  'with version ' + tuner_config.version + \
                  'is not supported.'
            
    #----------------------------------------------------------------------
    def _extractConfigData(self, tuner_config):
        """"""
        
        d = {}
        
        if not tuner_config.has_key('data'):
            print 'ERROR: Loaded dict must have the key "data".'
            return {}
        else:
            d['knobGroupList'] = tuner_config['data']
            
        if not isinstance(d['knobGroupList'], KnobGroupList):
            print 'ERROR: Loaded data object is not an ' + \
                  'object of class KnobGroupList.'
            return {}
            
        if tuner_config.has_key('name'):
            d['config_name'] = tuner_config['name']
        else:
            d['config_name'] = ''
                
        if tuner_config.has_key('config_description'):
            d['config_description'] = \
                tuner_config['config_description']
        else:
            d['config_description'] = ''

        if tuner_config.has_key('preferences'):
            pref = tuner_config['preferences']
            if pref.has_key(self._getSenderKey()):
                d['visible_col_list'] = \
                    pref[self._getSenderKey()][
                        'visible_column_name_list']
            else:
                d['visible_col_list'] = []
        else:
            d['visible_col_list'] = []
        
        return d
    
    
    #----------------------------------------------------------------------
    def saveSnapshotFile(self, model):
        """"""
        
        caption = 'Save Tuner Snapshot File'
        selected_filter_str = ('Tuner snapshot files (*' + 
                               self.fileExt_SnapshotFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getSaveFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)
        
        
        if filename[-len(self.fileExt_SnapshotFile):] != \
           self.fileExt_SnapshotFile:
            filename = filename + self.fileExt_SnapshotFile
            
        self.starting_directory_path = filename
        
        model._takeSnapshot()
            
        # After successful PV updates, save the latest
        # PV information to the file.
        snapshot = self._createSnapshotDict(model)
        f = open(filename, 'w')
        cPickle.dump(snapshot, f)
        f.close()
                        
    
    #----------------------------------------------------------------------
    def loadSnapshotFile(self, model_to_be_replaced):
        """"""
        
        caption = 'Load Tuner Snapshot File'
        selected_filter_str = ('Tuner snapshot files (*' + 
                               self.fileExt_SnapshotFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getOpenFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)
        
        
        self.starting_directory_path = filename
            
        f = open(filename, 'r')
        try:
            snapshot = cPickle.load(f)
        except: # catch all exceptions
            print 'Unpickling the file failed. ' + \
                  'You probably did not select a ' + \
                  'pickled file.'
            return
        finally:
            f.close()
            
        if type(snapshot) != dict:
            print 'ERROR: Loaded data object is not a dict.'
            return
            
        if not snapshot.has_key('version'):
            print 'ERROR: Loaded dict must have the key "version".'
            return
            
        if snapshot['version'] == '0.1.0':
            
            if not snapshot.has_key('tuner_config'):
                print 'ERROR: Loaded snapshot dict must have the key "tuner_config".'
                return
            else:
                tuner_config = snapshot['tuner_config']
            
            extracted_config_data = \
                self._extractConfigData(tuner_config)
            
            if not extracted_config_data:
                return
            
            extracted_snapshot_data = \
                self._extractSnapshotData(snapshot)
            
            if not extracted_snapshot_data:
                return
            
            self.emit(Qt.SIGNAL('snapshotFileLoaded'), 
                      model_to_be_replaced, 
                      extracted_config_data,
                      extracted_snapshot_data)
        else:
            print 'Loading of a tuner snapshot file ' + \
                  'with version ' + snapshot.version + \
                  'is not supported.'            
    
    #----------------------------------------------------------------------
    def _extractSnapshotData(self, snapshot):
        """"""
        
        d = {}
        d['flat_knob_list'] = snapshot['flat_knob_list']
        d['snapshot_read'] = snapshot['snapshot_read']
        d['snapshot_setp'] = snapshot['snapshot_setp']
        d['snapshot_read_timestamp'] = \
            snapshot['snapshot_read_timestamp']
        d['snapshot_setp_timestamp'] = \
            snapshot['snapshot_setp_timestamp']
        d['snapshot_description'] = \
            snapshot['snapshot_description']
   
        return d
    

    #----------------------------------------------------------------------
    def savePreferencesFile(self, visible_col_name_list):
        """"""
        
        caption = 'Save Tuner Preferences File'
        selected_filter_str = ('Tuner preferences files (*' + 
                               self.fileExt_TunerPrefFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getSaveFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)
        
        
        if filename[-len(self.fileExt_TunerPrefFile):] != \
           self.fileExt_TunerPrefFile:
            filename = filename + self.fileExt_TunerPrefFile
                
        self.starting_directory_path = filename
        
        preferences = self._createPreferencesDict(
            visible_col_name_list)
        f = open(filename, 'w')
        cPickle.dump(preferences, f)
        f.close()
            
    #----------------------------------------------------------------------
    def loadPreferencesFile(self):
        """"""
        
        caption = 'Load Tuner Preferences File'
        selected_filter_str = ('Tuner preferences files (*' + 
                               self.fileExt_TunerPrefFile + ')')
        filter_str = (selected_filter_str + ';;' +
                      'All files (*)')
        qfilename = Qt.QFileDialog.getOpenFileName(
            None, caption, self.starting_directory_path, filter_str,
            selected_filter_str)
        filename = str(qfilename)
        
        
        self.starting_directory_path = filename
        
        f = open(filename, 'r')
        try:
            preferences = cPickle.load(f)
        except: # catch all exceptions
            print 'Unpickling the file failed. ' + \
                  'You probably did not select a ' + \
                  'pickled file.'
            return
        finally:
            f.close()
        
        if type(preferences) != dict:
            print 'ERROR: Loaded data object is not a dict.'
            return
            
        if not preferences.has_key('version'):
            print 'ERROR: Loaded dict must have the key "version".'
            return
     
        if preferences['version'] == '0.1.0':
            
            sender_key = self._getSenderKey()
            
            if preferences.has_key(sender_key):
                pref = preferences[sender_key]
            else:
                Qt.QMessageBox.critical(None, 'ERROR',
                    ('Invalid preference file has been selected. This ' +
                     'prefrence file contains preferences dictionary with ' + 
                     'keys: ' + str(preferences.keys())) )
                return
            
            visible_column_name_list = \
                pref['visible_column_name_list']
            
            self.emit(Qt.SIGNAL('readyForUpdateOnPrefChange'),
                      visible_column_name_list)
            
        else:
            print 'Loading of a tuner preferences file ' + \
                  'with version ' + preferences.version + \
                  'is not supported.' 
    
        
    #----------------------------------------------------------------------
    def _finalizeConfigFromSetupGUI(self, model,
                                    saveFileFlag):
        """"""
        
        tuner_config = self._createConfigDict(model)
        config_data = self._extractConfigData(tuner_config)
        
        self.emit(Qt.SIGNAL('finalizedConfigFromSetupGUI'),
                  config_data, saveFileFlag)