# -*- coding: utf-8 -*-

"""
Example script for automatically performing a complete Metashape (MS) workflow 
on images from UAV campaigns with the M2EA drone.

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
# analysis from M2EA drone data.

def M2EA_workflow(config_data: dict,
                  prj_dir:     str,
                  img_dir:     str,
                  config_name: str):

###############################################################################
#####
##### parameters for point cloud classification
    class_usage = config_data['metashape']['point_cloud']['classification']['use']
    class_type  = config_data['metashape']['point_cloud']['classification']['type']
    class_set   = config_data['metashape']['point_cloud']['classification']['set']
    max_angle   = config_data['metashape']['point_cloud']['classification']['max_angle']
    max_dist    = config_data['metashape']['point_cloud']['classification']['max_distance']
    cell_size   = config_data['metashape']['point_cloud']['classification']['cell_size']
    test_set    = {'max_angle': max_angle, 'max_distance': max_dist, 'cell_size': cell_size}
    
    if class_type == 'test':
        classPC = (class_usage, class_type, test_set)
    else:
        classPC = (class_usage, class_type, class_set)

##### parameters for the photogrammetric workflow
    setMarkers_manually  = config_data['input']['marker_reference']['set_marker_manu']
    addMarkers_from_file = config_data['input']['marker_reference']['use_GCP_proj']
    addGCP_georef        = config_data['input']['marker_reference']['use_GCP_meas']
    GCP_import_format    = config_data['input']['marker_reference']['format']
    GCP_coord_system     = config_data['metashape']['reference']['measurement']['marker_crs']
    set_reference        = config_data['metashape']['reference']['general']['use_ref']
    data_type            = config_data['metashape']['general']['type']
    output_coord_system  = config_data['metashape']['export']['ortho_crs']
    export_list          = config_data['metashape']['export']['type']
    filter_noise         = config_data['metashape']['point_cloud']['filter']['noise']
    filter_ground        = config_data['metashape']['point_cloud']['filter']['ground']
    filter_unclass       = config_data['metashape']['point_cloud']['filter']['unclass']
    render_preview       = config_data['metashape']['point_cloud']['filter']['preview']

    if config_data['input']['image']['format']['conv'][0] == True:
        image_format = config_data['input']['image']['format']['conv'][1]
    else:
        image_format = config_data['input']['image']['format']['raw']
    
###############################################################################
#####
##### (0) create an instance of a drone project (UAV)
    MultiProject = ppp.DroneProject(config_data   = config_data, 
                                    project_dir   = prj_dir, 
                                    image_dir     = img_dir,
                                    config_name   = config_name)

###############################################################################
##### Photogrammetric image analysis workflow for the drone project
#####
##### (1) add photos into the active chunk
    MultiProject.addPhotosToChunk(image_dir    = img_dir,
                                  file_format  = image_format,
                                  layout       = ms.UndefinedLayout,
                                  save_project = (True, MultiProject.chunk.label))

##### (2) match photos
    if data_type == "RGB":
        detail_level = 1; key_points = 40000; tie_points = 4000
    if data_type == "IR":
        detail_level = 0; key_points = 10000; tie_points = 2000

    MultiProject = ppp.matchPhotos(project                = MultiProject,
                                   downscale              = detail_level,
                                   generic_preselection   = False,
                                   reference_preselection = True,
                                   keypoint_limit         = key_points,
                                   tiepoint_limit         = tie_points,
                                   save_project           = (True, MultiProject.chunk.label))

##### (3) align Cameras
    MultiProject = ppp.alignCameras(project          = MultiProject,
                                    adaptive_fitting = True,
                                    save_project     = (True, MultiProject.chunk.label))

##### (OPTIONAL) add markers manually to the active chunk
    if setMarkers_manually == True:
        
        if MultiProject.drone_IR == True:
            MultiProject.applyVegetationIndex(config_data  = config_data,
                                              save_project = (True, MultiProject.chunk.label))        

        MultiProject = ppp.Reference.set_marker_manually(project      = MultiProject,
                                                         config_data  = config_data,
                                                         save_project = (True, MultiProject.chunk.label))

##### (OPTIONAL) import marker projections
    if addMarkers_from_file == True:
        MultiProject = ppp.Reference.import_marker_proj(project      = MultiProject,
                                                        coord_system = GCP_coord_system,
                                                        optimize_cam = False,
                                                        save_project = (True, MultiProject.chunk.label))

##### (OPTIONAL) import real-world coordinates for markers
    if addGCP_georef == True:        
        MultiProject = ppp.Reference.import_marker_coord(project        = MultiProject,
                                                         coord_system   = GCP_coord_system,
                                                         optimize_cam   = False,
                                                         path           = MultiProject.GCP_path,
                                                         format         = ms.ReferenceFormatCSV,
                                                         create_markers = True, 
                                                         skip_rows      = 1,
                                                         columns        = GCP_import_format, 
                                                         delimiter      = ',',
                                                         save_project   = (True, MultiProject.chunk.label))

##### (OPTIONAL) set reference parameters for the chunk
    if set_reference == True:
        MultiProject = ppp.Reference.set_reference_param(project      = MultiProject, 
                                                        config_data  = config_data,
                                                        optimize_cam = True,
                                                        save_project = (True, MultiProject.chunk.label))

##### (4) build Depth Map
    MultiProject = ppp.buildDepthMaps(project       = MultiProject, 
                                      downscale     = 1,
                                      max_neighbors = 16,
                                      filter_mode   = ms.FilterMode.MildFiltering,
                                      save_project  = (True, MultiProject.chunk.label))

##### (5) build Point Cloud
    MultiProject = ppp.buildPointCloud(project          = MultiProject,
                                       point_colors     = True,
                                       point_confidence = True,
                                       max_neighbors    = 100,
                                       save_project     = (True, MultiProject.chunk.label))

# ##### (OPTIONAL) classify point cloud within a new added chunk    
    if type(classPC) == list and classPC[0][0] == True:        
        for i, item in enumerate(classPC):
            MultiProject.chunk.copy()
            MultiProject.doc.chunks[-1].label = f'classified_{classPC[i][1]}{i+1}'
        
    if type(classPC) == tuple and classPC[0] == True:
        MultiProject.chunk.copy()
        
        if classPC[1] == 'test': chunk_name = f'classified_{classPC[1]}'
        else:                    chunk_name = f'classified_{classPC[1]}_{classPC[2]}'
        
        MultiProject.doc.chunks[-1].label = chunk_name
        classPC = [classPC]

    for i, active_chunk in enumerate(MultiProject.doc.chunks[MultiProject.chunk_ID:]):

        MultiProject.chunk = active_chunk
        
        print(f'\nActive chunk for next MS workflow steps: {active_chunk.label}\n')
        
        if not 'unclassified' in active_chunk.label:
            
            MultiProject = ppp.PointCloud.Classification.classify_point_cloud(project      = MultiProject,
                                                                              class_param  = classPC[i-1],
                                                                              save_project = (True, active_chunk.label))
            
            MultiProject = ppp.PointCloud.Filter.filter_from_list(project           = MultiProject,
                                                                  filter_unclass    = filter_unclass,
                                                                  filter_high_noise = filter_noise,
                                                                  filter_ground     = filter_ground,
                                                                  render_preview    = render_preview,
                                                                  save_project      = (True, active_chunk.label))

##### (6) generate 3D model
        MultiProject = ppp.buildModel(project       = MultiProject,
                                      interpolation = ms.Interpolation.DisabledInterpolation,
                                      surface_type  = ms.SurfaceType.HeightField,
                                      save_project  = (True, active_chunk.label))
    
##### (7) generate digital elevation model (DEM)
        MultiProject = ppp.buildDem(project       = MultiProject,
                                    interpolation = ms.Interpolation.DisabledInterpolation,
                                    save_project  = (True, active_chunk.label))

##### (8) build UV mapping for the model
        MultiProject = ppp.buildUV(project      = MultiProject,
                                   save_project = (True, active_chunk.label))

##### (9) create orthomosaic (orthorectified projection)
        MultiProject = ppp.buildOrthoProjection(project      = MultiProject, 
                                                coord_system = ms.CoordinateSystem(output_coord_system),
                                                fill_holes   = False,
                                                save_project = (True, active_chunk.label))

##### (OPTIONAL) apply raster transformation specifications
        MultiProject.applyVegetationIndex(config_data  = config_data,
                                          save_project = (True, active_chunk.label))
   
##### (OPTIONAL): export project results
        ppp.Export.export_from_list(project     = MultiProject, 
                                    export_list = export_list)

##### (Finally): return the final project instance
    return MultiProject