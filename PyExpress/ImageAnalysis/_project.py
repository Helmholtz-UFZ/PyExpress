# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

import PyExpress.UtilityTools  as hlp
import PyExpress.ImageAnalysis as ppp

try:
    import os
    import re
    import sys
    import shutil
    import time
    import Metashape
    from   abc import ABC
except Exception as e:
    print("Some modules are missing {}".format(e))

class _MetashapeProject(ABC):
    def __init__(self, 
                 config_data:        dict,
                 project_dir:        str,
                 image_dir:          str,
                 config_name:        str):

        # config to class object
        self._config_to_object(config_data=config_data)
        
        # check Metashape program version
        # enable/disable GPU memory support; as well as CPU support for GPU usage
        ppp.metashape_initial_check(version_GUI = self.config.metashape.initialization.GUIversion, 
                                    enable_GPU  = self.config.metashape.initialization.enableGPU, 
                                    enable_CPU  = self.config.metashape.initialization.enableCPU)

        # projectID generation
        self._create_projectID(config_data=config_data, file_name=config_name)
        
        # project status setting   
        new_project    = self.config.input.general.new_project
        if new_project == True:  self.project_status = 'new'
        if new_project == False: self.project_status = 'existing'

        # UAV specific settings
        if self.drone_IR == True or self.drone_RGB == True:
            self._set_reference_path(config_data=config_data)

        # initialitation of project and subdirectories
        self.project_dir = project_dir
        self.image_dir   = image_dir
        self.save_dir    = os.path.join(project_dir,'project_data')
        self.export_dir  = os.path.join(project_dir,'export_data')
        self.log_dir     = os.path.join(project_dir,'export_data')
        self.config_name = config_name

        # define some empty parameter types to fill with content later
        self.extensive_logging   = self.config.metashape.document.logging
        self.vegetation_index    = 'B1'
        self.image_format_raw    = self.config.input.image.format.raw
        self.image_format_conv   = ''
        if self.config.input.image.format.conv[0] == 'True':
            self.img_format_conv = self.config.input.image.format.conv[1]
        
        # creates/deletes/overwrites a metashape projectID directory structure
        if self.project_status == 'new':
            self._check_directory(path=self.save_dir,   projectID=self.project_ID)
            self._check_directory(path=self.export_dir, projectID=self.project_ID)
            self._save_count = 0
        if self.project_status == 'existing':
            self._save_count = 1
        
        # creates or openes a Metashape project including working chunk
        if self.project_status == 'new':
            self.doc         = Metashape.Document()    # Create empty Metashape instance
            self.chunk       = self.doc.addChunk()   # Create chunk in that Document
            self.chunk.label = self.config.metashape.chunk.label
            self.chunk_ID    = 0
            self.logging(f'Created projectID: {self.project_ID}')

        elif self.project_status == 'existing':
            self.export_dir = f'{self.export_dir}\\{self.project_ID}'
            self.log_dir    = f'{self.log_dir}\\{self.project_ID}'

            self.doc         = Metashape.Document()
            self.read_only   = self.config.metashape.document.read_only
            self.ignore_lock = self.config.metashape.document.ignore_lock
            self.chunk_ID    = self.config.metashape.chunk.ID_active
            new_chunk_label  = self.config.metashape.chunk.label
                
            if self.read_only == True:
                ask = input('Saving is disabled in read only mode. Change to editing mode [y,n]?: ')
                if ask == 'y': self.read_only = False
            try:
                path = os.path.join(self.save_dir, self.project_ID+'.psx')
                self.doc.open(path        = path, 
                              read_only   = self.read_only, 
                              ignore_lock = self.ignore_lock)
                if self.chunk_ID == 999:
                    if new_chunk_label in [a.label for a in self.doc.chunks]:
                        print(f'Chosen label "{new_chunk_label}" of created chunk already exists in the chunk list\n'
                              f'--> renaming to "{new_chunk_label}_new"')
                        new_chunk_label = f'{new_chunk_label}_new'
                    self.chunk       = self.doc.addChunk()
                    self.chunk.label = new_chunk_label
                    self.chunk_ID    = len(self.doc.chunks) - 1
                else:
                    self.chunk = self.doc.chunks[self.chunk_ID]
            except:
                sys.exit(f'\nException: \nProject {self.project_ID}.psx does not exist.')
            
            self.logging(f'Opened project with ID: {self.project_ID}'
                         f'\n    read_only: {self.read_only}'
                         f'\n    ignore_lock: {self.read_only}')


    # MAIN LOGGING FUNCTION --> ...\exportData\projectID\process_log.txt

    def logging(self, msg: str):
        
        '''
        Generates a terminal log and saves it with an additional timestamp in the project log file.

        *args:
            msg: message to be logged in the protocol file
        '''

        if self.extensive_logging == False:
            return
        
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        logfile = open(self.log_dir + "/process_log.txt", "a")
        logfile.write(time.strftime("%d.%m.%Y %H:%M:%S ") + msg + "\n")
        logfile.close()


    # INITIAL DIRECTORY CHECK AND CREATION

    def _create_directory(self, path: str):
        
        '''
        Creates a directory for the specified path if it does not already exist.

        *args:
            path: path to a directory that is to be created

        Returns:
            Boolean indicating whether the path already exists.
        '''

        if os.path.dirname(path) == self.export_dir:
            dirname         = os.path.dirname(path)
            basename        = os.path.basename(path).split('.')[0]            
            makeDir         = f'{dirname}\\{basename}'
            self.export_dir = makeDir
            self.log_dir    = makeDir
        
        if os.path.dirname(path) == self.save_dir:
            makeDir  = os.path.dirname(path)
            
        if not os.path.exists(path):
            os.makedirs(makeDir, exist_ok=True)
            return False
        else:
            return True


    # CLEAN AN EXISTING DIRECTORY
    
    def _clear_directory(self, path: str, projectID: str):
        
        '''
        Clears the specified directory based on a projectID and additionally unlinks all files.

        *args:
            path: relative directory path\n
            projectID: specific projectID/name of a Metashape project
        '''
        
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if projectID in name:
                    os.remove(os.path.join(root, name))
            for name in dirs:
                if projectID in name:
                    shutil.rmtree(os.path.join(root, name))


    # CHECK EXISTENCE AND CONTENT OF A DIRECTORY

    def _check_directory(self, path: str, projectID: str):
        
        '''
        Checks if a specific project ID name/directory exists in a designated directory.
        If yes, it will be cleared if possible; if not, the directory will be created.

        *args:
            path: relative directory path\n
            projectID: specific projectID/name of a Metashape project
        '''

        if path == self.save_dir:
            _path  = f'{path}\\{projectID}.psx'
            exists = self._create_directory(_path)
        
        if path == self.export_dir:
            _path  = f'{path}\\{projectID}'
            exists = self._create_directory(_path)

        if exists == True:
            self._clear_directory(path, projectID)


    # PROJECT ID

    def _create_projectID(self, config_data: dict, file_name: str):
        
        ''' 
        Creates a Metashape Project ID from the metadata of your image acquisition campaign
        or a specified string.
        
        *args: 
            config_data: content of the project configuration file\n
            file_name: filename from which you want to create a Project ID
        '''

        projectID_genType    = config_data['input']['general']['ID_source']
            
        if self.stereo_IR == True or self.stereo_RGB == True:
            
            if projectID_genType == 'campaign':                
                meta      = config_data['input']['campaign']
                projectID = '_'.join((meta['date'], meta['location'], 
                                      meta['cameraID'], meta['channel'], meta['ID_info']))
                projectID = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', projectID))
        
        if self.drone_IR == True or self.drone_RGB == True:
        
            if projectID_genType == 'campaign':
                meta      = config_data['input']['campaign']        
                projectID = '_'.join((meta['date'], meta['time'], meta['location'],
                                          meta['drone'], meta['sensor'], meta['ID_info']))
                
                projectID = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', projectID))
        
        if projectID_genType == 'string':            
            projectID = config_data['input']['general']['ID_string']
        
        # if projectID_genType == 'existing':
        #     fname = os.path.basename(file_name)
        #     projectID = os.path.splitext(fname)[0]

        self.project_ID = projectID


    # SET CLASS PARAMETERS FROM CONFIG FILE
    
    def _config_to_object(self, config_data: dict):
        
        '''
        Transfers the parameters from the configuration file into class internal objects.
        
        *args:
            config_data: content of the project configuration file
        '''
        
        self.config = type('Configuration', (), {})()
        
        def dict_to_attr(config_data, parent=None):
            if parent is None:
                parent = self.config
            
            for key, value in config_data.items():
                
                if isinstance(value, dict):
                    sub_obj = type(key, (), {})()
                    setattr(parent, str(key), sub_obj)
                    dict_to_attr(value, sub_obj)
                else:
                    setattr(parent, str(key), value)
        
        dict_to_attr(config_data)


    # SET FILE PATHS FOR GEOREFERENCING

    def _set_reference_path(self, config_data: dict):

        ''' 
        Defines data paths for georeferencing UAV project images. 
        
        *args: 
            config_data: content of the project configuration file
        '''

        # Adding reflectance panel path: file where reflectance panel specifications are store
        if config_data['input']['reflectance']['reflectancepanel_path']:
            self.reflect_panel_path = config_data['input']['reflectance']['reflectancepanel_path']
            
        # Adding GCP path: file where GCP reference locations are stored
        if config_data['input']['marker_reference']['reference_path']:
            self.GCP_path           = config_data['input']['marker_reference']['reference_path']
         
        # Adding marker projection path
        if config_data['input']['marker_reference']['projections_path']:
            self.marker_proj_path   = config_data['input']['marker_reference']['projections_path']


    # SAVE METASHAPE DOCUMENT

    def saveMetashapeProject(self, active_chunk: str='unclassified'):
        
        '''
        Saves the current Metashape project data to the ProjectData directory in the working environment. 
        Reloads the project instance and sets the specified chunk as active, which is necessary due to Agisoft Metashape.

        *args:
            active_chunk: label of the active chunk in the MS project
        '''
        
        active_chunk = [a.label for a in self.doc.chunks].index(active_chunk)

        if self._save_count==0:
            if hasattr(self, 'project_ID'):
                self.doc.save(f'{self.save_dir}\\{self.project_ID}.psx')
                self.chunk = self.doc.chunks[active_chunk]

            elif not hasattr(self, 'project_ID'):
                timestring = time.strftime('%d.%m.%Y_%Hhh%Mmm', time.localtime(time.time()))
                self.doc.save(f'{self.save_dir}\\{timestring}.psx')
                self.chunk = self.doc.chunks[active_chunk]

            self._save_count += 1
            self.logging(f"Metashape project saved to {self.save_dir}")

        else:
            self.doc.save()
            self.chunk = self.doc.chunks[active_chunk]

            self._save_count += 1
            self.logging("Metashape project saved")


    # LOAD IMAGES

    def _loadingImages(self, image_dir: str, file_format: str):
        
        ''' 
        Loads a set of images from a specified normal directory into a list.

        *args:
            image_dir: absolute path to your image folder\n
            file_type: image format, e.g. JPG, TIFF, PNG, RAW, ...

        Returns:
            List of images
        '''

        listOfFiles      = list()
        
        for (dirpath, dirnames, filenames) in os.walk(image_dir):
            for filename in filenames:
                if filename.lower().endswith(file_format.lower()):
                    listOfFiles.append(os.path.normpath(f'{image_dir}\\{filename}'))

        if not listOfFiles:
            self.logging(f'ERROR: No {file_format} files found in image_dir directory.')
            sys.exit(f'ERROR: no files of type {file_format} found in {image_dir}')
            
        return listOfFiles


    # ADD PHOTOS TO ACTIVE PROJECT CHUNK
    
    def addPhotosToChunk(self,
                         image_dir:    str, 
                         file_format:  str,
                         save_project: tuple = (False, ''),
                         **kwargs):
        
        '''
        Adds photos to the active chunk of your Metshape project instance/doc.

        *args:
            image_dir: absolute path to your image folder\n
            file_format: image format; supported formats see below\n
            save_project: (True/False, *active_chunk*.label)
    
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n
            addPhotos   --> class Metashape.Chunk.addPhotos\n
            imageFormat --> class Metashape.ImageFormat
        '''

        start_time = time.time()
        
        photoList = self._loadingImages(image_dir, file_format)
        
        if self.stereo_RGB == True:
            print(f'Metashape workflow: (1) adding image folder to chunk (num: {len(photoList)})')
            self.logging(f'Adding {len(photoList)} stereo images to chunk {self.chunk.label}')
        
        elif self.stereo_IR == True:
            print(f'Metashape workflow: (1) adding image folder to chunk (num: {len(photoList)})')
            self.logging(f'Adding {len(photoList)} stereo images to chunk {self.chunk.label}')
        
        elif self.drone_IR == True:
            print(f'Metashape workflow: (1) adding photos to chunk (num: {len(photoList)})')
            self.logging(f'Adding {len(photoList)} images to chunk {self.chunk.label}')

        elif self.drone_RGB == True:
            print(f'Metashape workflow: (1) adding photos to chunk (num: {len(photoList)})')
            self.logging(f'Adding {len(photoList)} images to chunk {self.chunk.label}')
            
        self.chunk.addPhotos(filenames=photoList, **kwargs)
        
        if save_project[0] == True:            
            self.saveMetashapeProject(active_chunk=save_project[1])
        
        hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')