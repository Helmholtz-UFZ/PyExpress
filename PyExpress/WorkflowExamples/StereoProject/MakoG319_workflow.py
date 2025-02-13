# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Example script for automatically performing a complete Metashape (MS) workflow 
on data from rigidly installed cameras within a stereo setup of Mako319 cameras
from Allied Vision.

@author: Martin Kobe, martin.kobe@ufz.de; Rikard Graß, rikard.grass@ufz.de

@status: 11/2024; part of the EXPRESS Project at UFZ Leipzig.

*******************************************************************************
NOTE: (a) Each single function in the MS main workflow, marked by numbers, is 
      adapted from the GUI of MS by using the Python API. Therefore, key word 
      arguments can be adapted/inserted according to the user manual:
      https://www.agisoft.com/pdf/metashape_python_api_2_1_2.pdf
      
      (b) Optional functions are specifically written for the needs of this 
      workflow but are also highly usable for other applications of the same 
      kind. If you intend to integrate additional functionalities, please 
      consult the authors of PyExpress.
"""

###############################################################################
# Import of necessary modules
try:
    import Metashape as ms
    import PyExpress.ImageAnalysis as ppp

except Exception as e:
    print("Some modules are missing {}".format(e))
    

###############################################################################
# Main function for a fully automated photogrammetric workflow for image 
# analysis from rigid camera installations, utilizing the dynamic 4D frame
# analysis functionality of Metashape.

def MakoG319_workflow(config_data: dict,
                      prj_dir:     str,
                      img_dir:     str,
                      config_name: bool=False):

###############################################################################
#####
##### (0) create an instance of a Metashape multiframe (stereo) project    
    StereoProject = ppp.StereoProject(config_data  = config_data, 
                                      project_dir  = prj_dir,
                                      image_dir    = img_dir,
                                      config_name  = config_name)

###############################################################################
##### Metashape workflow for a stereo camera project
#####
##### (1) add photos into the active chunk and rename the frame groups
    camSetup = config_data['metashape']['setup']['cameras']
    
    if config_data['input']['image']['format']['conv'][0] == True:
        image_format = config_data['input']['image']['format']['conv'][1]
    else:
        image_format = config_data['input']['image']['format']['raw']
        
    for cam in camSetup:
        StereoProject.addPhotosToChunk(image_dir    = f'{img_dir}\\{cam}', 
                                       file_format  = image_format, 
                                       layout       = ms.MultiframeLayout,
                                       save_project = (True, StereoProject.chunk.label))

    for i, cam in enumerate(camSetup):
        StereoProject.chunk.cameras[i].label = f'undistorted_stereoCam_{cam}'

##### (OPTIONAL) set calibration parameters for each optical sensor in the chunk
    StereoProject = ppp.Calibration.set_sensor_param_stereo(project      = StereoProject,
                                                            config_data  = config_data,
                                                            save_project = (True, StereoProject.chunk.label))

##### (OPTIONAL) set reference parameters for the chunk
    StereoProject = ppp.Reference.set_reference_param(project      = StereoProject, 
                                                      config_data  = config_data,
                                                      optimize_cam = False,
                                                      save_project = (True, StereoProject.chunk.label))
    
##### (OPTIONAL) set location parameters for each optical sensor in the chunk
    StereoProject = ppp.Reference.set_camera_param(project      = StereoProject, 
                                                   config_data  = config_data,
                                                   optimize_cam = False,
                                                   save_project = (True, StereoProject.chunk.label))

##### (OPTIONAL) create a scalebar between two sensors in the chunk
    distance  = config_data['metashape']['reference']['scalebar']['dist']
    accuracy  = config_data['metashape']['reference']['scalebar']['acc']
    enable    = config_data['metashape']['reference']['scalebar']['enable']
    image_IDs = config_data['metashape']['reference']['scalebar']['image_IDs']

    StereoProject = ppp.Reference.add_scalebar(project      = StereoProject,
                                               distance     = distance,
                                               accuracy     = accuracy,
                                               enable       = enable,
                                               image_IDs    = image_IDs,
                                               save_project = (True, StereoProject.chunk.label))
 
##### (2) match photos    
    StereoProject = ppp.matchPhotos(project                      = StereoProject,
                                    downscale                    = 0,
                                    generic_preselection         = True,
                                    reference_preselection       = True,
                                    reference_preselection_mode  = ms.ReferencePreselectionSource,
                                    keypoint_limit               = 40000,
                                    tiepoint_limit               = 10000,
                                    guided_matching              = False,
                                    reset_matches                = True,
                                    mask_tiepoints               = False,
                                    filter_stationary_points     = False,
                                    save_project                 = (True, StereoProject.chunk.label))

##### (3) align Cameras
    StereoProject = ppp.alignCameras(project            = StereoProject,
                                     reset_alignment    = True,
                                     adaptive_fitting   = False,
                                     subdivide_task     = True,
                                     save_project       = (True, StereoProject.chunk.label))

##### (OPTIONAL) optimize cameras for tie point covariance calculation
    StereoProject = ppp.Reference.optimize_cameras(project = StereoProject, update_transform = True,
                                                   fit_f   = False, fit_cx = False, fit_cy = False,
                                                   fit_b1  = False, fit_b2 = False, fit_k1 = False, 
                                                   fit_k2  = False, fit_k3 = False, fit_k4 = False, 
                                                   fit_p1  = False, fit_p2 = False, fit_corrections = False,
                                                   adaptive_fitting = False, tiepoint_covariance = True,
                                                   save_project = (True, StereoProject.chunk.label))

##### (OPTIONAL) redefine bounding box to a maximum extent according to tie point occurence in 4D frames
    StereoProject = ppp.BBox.redefine_auto_multiframe(project      = StereoProject, 
                                                      reference_ID = 0,
                                                      save_project = (True, StereoProject.chunk.label))

##### (OPTIONAL) gradually remove tie points exceeding a threshold of error
    StereoProject = ppp.TiePointCloud.Filter.gradual_removal(project      = StereoProject,
                                                             criterion    = ms.TiePoints.Filter.ProjectionAccuracy,  # MS version > 2.0.0
                                                             threshold    = 5,
                                                             save_project = (True, StereoProject.chunk.label))

##### (4) build Depth Map    
    StereoProject = ppp.buildDepthMaps(project           = StereoProject, 
                                       downscale         = 1,
                                       max_neighbors     = 1,
                                       subdivide_task    = False,
                                       filter_mode       = ms.FilterMode.MildFiltering,
                                       save_project      = (True, StereoProject.chunk.label))

##### (5) build Point Cloud
    StereoProject = ppp.buildPointCloud(project          = StereoProject,
                                        point_colors     = True,
                                        point_confidence = True,
                                        save_project     = (True, StereoProject.chunk.label))

##### (7) generate digital elevation model (DEM)
    StereoProject = ppp.buildDem(project       = StereoProject,
                                 interpolation = ms.Interpolation.DisabledInterpolation,
                                 save_project  = (True, StereoProject.chunk.label))

##### (OPTIONAL) export results - precision map
    ppp.Export.precision_map(project       = StereoProject,
                             pattern       = r'(\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m\d{2}s)',
                             export_format = 'txt')

##### (OPTIONAL) export results - point cloud
    ppp.Export.point_cloud(project               = StereoProject,
                           pattern               = r'(\d{4}-\d{2}-\d{2}_\d{2}h\d{2}m\d{2}s)',
                           source_data           = ms.PointCloudData,     # MS vs > 2.0.0
                           binary                = True,
                           save_point_normal     = True, 
                           save_point_color      = True, 
                           save_point_confidence = True, 
                           colors_rgb_8bit       = True,
                           format                = ms.PointCloudFormatPLY, # MS vs > 2.0.0
                           crs                   = StereoProject.chunk.crs)


##### (Finally): return the final project instance
    return StereoProject