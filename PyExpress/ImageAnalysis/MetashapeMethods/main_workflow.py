# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

from PyExpress.ImageAnalysis import _MetashapeProject

try:
    import time
    import Metashape
    import PyExpress.UtilityTools as hlp
except Exception as e:
    print("Some modules are missing {}".format(e))


##########################################################################################
# 1. MATCH PHOTOS

def matchPhotos(project:      object,
                save_project: tuple = (False, ''),
                **kwargs):

    ''' Performs image matching for each frame in the active Metashape chunk.

    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.matchPhotos

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
    
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])
    
    # ensure, that argument project is an instance of _MetashapeProject-class
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.' +
                        'Like the MultispectralProject or RGBProject classes.')
    
    # print workflow step and log photo matching parameters
    print('Metashape workflow: (2) matching photos')    
    project.logging(f'Matching Photos:\n{arguments_string}')

    # match photos
    if project.stereo_RGB == True or project.stereo_IR == True:  
        for frame in project.chunk.frames:
            frame.matchPhotos(**kwargs)    
    else:
        project.chunk.matchPhotos(**kwargs)

    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 2. ALIGN CAMERAS

def alignCameras(project:      object, 
                 save_project: tuple = (False, ''),
                 **kwargs):
    
    ''' Performs image alignment for the active Metashape chunk.

    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)
        
    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.alignCameras

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
        
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])

    # ensure, that argument project is an instance of _MetashapeProject-class    
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.' +
                        'Like the MultispectralProject or RGBProject classes.')

    # print workflow step and log photo alignment parameters
    print('Metashape workflow: (3) aligning cameras')    
    project.logging(f'Aligning Cameras:\n{arguments_string}')

    # align cameras
    project.chunk.alignCameras(**kwargs)
        
    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')

    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 3. BUILD DEPTH MAP

def buildDepthMaps(project:      object, 
                   save_project: tuple = (False, ''),
                   **kwargs):
    
    ''' Builds a depth map from the matched photos for each frame in the active Metashape chunk.

    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.buildDepthMaps

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
        
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])

    # ensure, that argument project is an instance of _MetashapeProject-class    
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.' +
                        'Like the MultispectralProject or RGBProject classes.')
    
    # print workflow step and log parameters of depth map calculation
    print('Metashape workflow: (4) building depth map')    
    project.logging(f'Building DepthMap:\n{arguments_string}') 
    
    # create depth map
    if project.stereo_RGB == True or project.stereo_IR == True:        
        for frame in project.chunk.frames:
            frame.buildDepthMaps(**kwargs)            
    else:
        project.chunk.buildDepthMaps(**kwargs)
        
    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 4. BUILD DENSE/POINT CLOUD

def buildPointCloud(project:      object,
                    save_project: tuple = (False, ''),
                    **kwargs):

    ''' Builds a dense point cloud for each frame in the active Metashape chunk.\n
    !!! Since Metashape version 2.0.0, Densecloud was renamed to Pointcloud !!!
    
    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.buildPointCloud

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
            
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])

    # ensure, that argument project is an instance of _MetashapeProject-class
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                        'Like the MultispectralProject or RGBProject classes.')

    # print workflow step and log parameters of point cloud creation
    print('Metashape workflow: (5) building point cloud')
    project.logging(f'Building PointCloud (MS: 2.x.x) / DenseCloud (MS: 1.x.x)\n{arguments_string}')

    # create dense cloud
    if str(Metashape.version)[0] == '1':
        project.chunk.buildDenseCloud(**kwargs)
            
    if str(Metashape.version)[0] == '2':
        project.chunk.buildPointCloud(**kwargs)

    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 5. BUILD 3D MODEL

def buildModel(project:      object,
               save_project: tuple = (False, ''),
               **kwargs):
    
    '''Builds a 3D model for each frame in the active Metashape chunk.
    
    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.buildModel

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
    
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])

    # ensure, that argument project is an instance of _MetashapeProject-class 
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                        'Like the MultispectralProject or RGBProject classes.')

    # print workflow step and log parameters for 3D model generation
    print('Metashape workflow: (6) generating 3D model')
    project.logging(f'Building 3D Model:\n{arguments_string}')

    # generate a model   
    if project.stereo_RGB == True or project.stereo_IR == True:      
        for frame in project.chunk.frames:
            frame.buildModel(**kwargs)            
    else:
        project.chunk.buildModel(**kwargs)

    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 6. BUILD DEM

def buildDem(project:      object,
             save_project: tuple = (False, ''),
             **kwargs):
    
    ''' Builds a Digital Elevation Model (DEM) for the active Metashape chunk.
    
    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.buildDEM

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
    
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])
 
    # ensure, that argument project is an instance of _MetashapeProject-class    
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                        'Like the MultispectralProject or RGBProject classes.')

    # print workflow step and log parameters of DEM generation
    print('Metashape workflow: (7) generating DEM')
    project.logging(f'Building 3D Model:\n{arguments_string}')

    # build the DEM
    project.chunk.buildDem(**kwargs)
        
    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 7. BUILD UV

def buildUV(project:      object,
            save_project: tuple = (False, ''),
            **kwargs):
 
    ''' Maps a 3D model's surface onto a 2D plane for texture application (UV mapping).
    
    *args:
        project: your Metashape project\n
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n\n
        --> class Metashape.Chunk.buildUV

    Returns:
        Updated Metashape project
    '''
    
    # time tracking
    start_time = time.time()
    
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])
    
    if not arguments_string: arguments_string = '    default settings'            
 
    # ensure, that argument project is an instance of _MetashapeProject-class    
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                        'Like the MultispectralProject or RGBProject classes.')
        
    # print workflow step and log parameters of UV mapping
    print('Metashape workflow: (8) building UV mapping')
    project.logging(f'Building uv mapping for the model:\n{arguments_string}')

    # build the UV mapping
    project.chunk.buildUV(**kwargs)
            
    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])

    return project


##########################################################################################
# 8. BUILD ORTHO PHOTOS

def buildOrthoProjection(project:      object,
                         coord_system:     object,
                         save_project: tuple = (False, ''),
                         **kwargs):
    
    ''' Creates an ortho projection (orthomosaic) for the active Metashape chunk.\n
    Please define a coordinate system for the metashape Project.\n 
    This is not required if you use georeferenced images or added GCP.

    *args:
        project: your Metashape project\n
        coord_system: 
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n
            --> class Metashape.CoordinateSystem
        save_project: (True/False, active_chunk.label)

    **kwargs:
        Get further information in the user manual:\n
        https://www.agisoft.com/downloads/user-manuals/\n
        --> class Metashape.Chunk.buildOrthomosaic

    Returns:
        Updated Metashape project
            
    '''
    
    # time tracking
    start_time = time.time()
    
    # get keyword arguments for generating keyword arguments string for logging
    arguments = dict()
    
    for key, value in kwargs.items():        
        arguments[key] = value

    arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])

    # ensure, that argument project is an instance of _MetashapeProject-class
    if not isinstance(project, _MetashapeProject):
        raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                        'Like the MultispectralProject or RGBProject classes.')

    # print workflow step and log parameters of the orthomosaic creation
    print('Metashape workflow: (9) creating orthomosaic')
    project.logging(f'Creating orthomosaic for the active chunk\n{arguments_string}')

    # add a projection on which basis a orthomosaic can be taken
    projection = Metashape.OrthoProjection()
    
    # check if model from chunk has a defined crs and if so add it to projection
    if coord_system:
        try:
            projection.crs = coord_system
        except:
            raise ValueError('Coordinate system must be Metashape.CoordinateSystem(...)')
    else:
        try:
            project.chunk.crs
            projection.crs = project.chunk.crs
        except:
            raise ValueError('Coordinate system missing. Please define (project.chunk.crs = ...)')

    # build ortho mosaic
    project.chunk.buildOrthomosaic(projection=projection, **kwargs)
        
    hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
    
    # save project and redefine the working chunk
    if save_project[0] == True:            
        project.saveMetashapeProject(active_chunk=save_project[1])
        
    return project