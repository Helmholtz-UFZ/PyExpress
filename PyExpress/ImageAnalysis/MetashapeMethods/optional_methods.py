# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

from PyExpress.ImageAnalysis import _MetashapeProject

try:
    import time, os, csv, math
    import Metashape
    import pandas                  as pd
    import numpy                   as np
    import PyExpress.ImageAnalysis as ppp
    import PyExpress.UtilityTools  as hlp
except Exception as e:
    print("Some modules are missing {}".format(e))


###############################################################################
# Export results of photogrammetric processing

class Export():

    def export_from_list(project: object,
                         export_list: list):

        ''' 
        Exports Metashape results from the active chunk specified by a list.\n
        The export uses default parameters without any keyword argument specifications.\n
        For more specific export options, please use the corresponding methods in the Export class.
        
        *args:
            project: your Metashape project\n
            export (case insensitive):\n
            ['camera', 'dem', 'dem_trafo', 'marker', 'model', 'ortho', 'ortho_trafo', 'point_cloud', 'precision_map', 'report', 'tiled_model'] \n
        
        *export_formats:
            Camera: XML\n
            DEM: TIFF\n
            DEM_trafo: basic raster transformed by value (_val.TIFF) and palette (_pal.TIFF)\n
            3DModel: OBJ\n
            Orthomosaic: TIFF\n
            Orthomosaic_trafo: basic raster transformed by value (_val.TIFF) and palette (_pal.TIFF)\n
            PointCloud: OBJ\n
            PrecisionMap: TXT\n
            Report: PDF\n
            TiledModel: OBJ\n
        '''

        # time tracking
        start_time = time.time()
        
        # print workflow step
        print('Metashape workflow: (OPT) exporting results from list')

        # export data according to entrys of the list 'export'
        
        if any(s.lower() == 'dem' for s in export_list):
            ppp.Export.raster(project      = project, 
                              export_type  = 'dem'.upper(),
                              source_data  = Metashape.DataSource.ElevationData,
                              image_format = Metashape.ImageFormatTIFF)
        
        if any(s.lower() == 'ortho' for s in export_list):
            ppp.Export.raster(project      = project, 
                              export_type  = 'ortho',
                              source_data  = Metashape.DataSource.OrthomosaicData, 
                              image_format = Metashape.ImageFormatTIFF) 

        if any(s.lower() == 'dem_trafo' for s in export_list):

            # ppp.Export.raster(project          = project, 
            #                   export_type      = 'dem'.upper()+'_transform_val',
            #                   save_alpha       = False,
            #                   raster_transform = Metashape.RasterTransformValue, 
            #                   source_data      = Metashape.DataSource.ElevationData,
            #                   image_format     = Metashape.ImageFormatTIFF)
                
            ppp.Export.raster(project          = project, 
                              export_type      = 'dem'.upper()+'_transform_pal',
                              save_alpha       = False,
                              raster_transform = Metashape.RasterTransformPalette, 
                              source_data      = Metashape.DataSource.ElevationData,
                              image_format     = Metashape.ImageFormatTIFF)
            
        if any(s.lower() == 'ortho_trafo' for s in export_list):

            # if project.drone_RGB == True or project.stereo_RGB == True:
            #     trafo_color = Metashape.RasterTransformPalette
            # else:
            #     trafo_color = Metashape.RasterTransformValue

            ppp.Export.raster(project          = project, 
                              export_type      = 'ortho_transform_val',
                              raster_transform = Metashape.RasterTransformValue,
                              save_alpha       = False,
                              source_data      = Metashape.DataSource.OrthomosaicData,
                              image_format     = Metashape.ImageFormatTIFF)

            ppp.Export.raster(project          = project, 
                              export_type      = 'ortho_transform_pal',
                              raster_transform = Metashape.RasterTransformPalette,
                              save_alpha       = False,
                              source_data      = Metashape.DataSource.OrthomosaicData,
                              image_format     = Metashape.ImageFormatTIFF)
            
        if any(s.lower() == 'model' for s in export_list):
            ppp.Export.model(project = project,
                             format  = Metashape.ModelFormatOBJ)
        
        if any(s.lower() == 'tiled_model' for s in export_list):
            ppp.Export.tiled_model(project = project,
                                   format  = Metashape.ModelFormatOBJ)
        
        if any(s.lower() == 'camera' for s in export_list):
            ppp.Export.camera(project = project,
                              format  = Metashape.CamerasFormatXML)
        
        if any(s.lower() == 'point_cloud' for s in export_list):
            if str(Metashape.version)[0] == '1':
                ppp.Export.point_cloud(project         = project,
                                       source_data     = Metashape.DataSource.DenseCloudData,
                                       format          = Metashape.PointsFormatOBJ,
                                       save_colors     = True, 
                                       colors_rgb_8bit = True)
            if str(Metashape.version)[0] == '2':        
                ppp.Export.point_cloud(project          = project,
                                       source_data      = Metashape.DataSource.PointCloudData,
                                       format           = Metashape.PointCloudFormatOBJ,
                                       save_point_color = True, 
                                       colors_rgb_8bit  = True)
        
        if any(s.lower() == 'precision_map' for s in export_list):
            ppp.Export.precision_map(project = project, 
                                     format  = 'txt')

        if any(s.lower() == 'report' for s in export_list):
            ppp.Export.report(project = project)
        
        if any(s.lower() == 'marker' for s in export_list):
            ppp.Export.marker(project       = project, 
                              export_format = 'xml')

        hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
        

    def marker(project: object, export_format='xml', **kwargs):
        
        '''
        Exports markers projections from the active chunk in either CSV or XML format or both.
        
        *args:
            project: your Metashape project\n
            export_format: ['csv', 'xml', 'both'] - export format of marker projections

        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportMarkers     
        '''
        
        export_csv, export_xml = False, False
        
        if export_format == 'csv':  export_csv = True
        if export_format == 'xml':  export_xml = True        
        if export_format == 'both': export_csv, export_xml = True, True  
            
        if export_csv == True:
            data          = []

            savepath_1    = f'{project.export_dir}\\{project.chunk.label}'
            export_path_1 = f'{savepath_1}\\marker_projections.csv'
                        
            savepath_2    = os.path.normpath(project.config.input.marker_reference.exp_marker_path)
            # saveID        = project.project_dir.split('\\')[-2]
            filename      = os.path.basename(savepath_2).split('.')[0]
            dirname       = os.path.dirname(savepath_2)
            # export_path_2 = f'{savepath_2}\\{saveID}_marker_projections.csv'
            export_path_2 = f'{dirname}\\{filename}.csv'

            os.makedirs(savepath_1, exist_ok=True)
            os.makedirs(savepath_2, exist_ok=True)
            
            for marker in project.chunk.markers:
                for camera in marker.projections.keys():
                    proj = marker.projections[camera]
                    if proj.pinned:
                        data.append([marker.label, camera.label, proj.coord.x, proj.coord.y])
                        
            for export_file in [export_path_1, export_path_2]:
                with open(export_file, 'w', encoding = 'UTF8', newline = '') as f:
                    writer = csv.writer(f)
                    writer.writerows(data)

        if export_xml == True:
         
            export_path = kwargs.pop('path', None)
            
            if export_path == None:
                export_path = f'{project.export_dir}\\{project.chunk.label}'        
                os.makedirs(export_path, exist_ok=True)
                export_path = f'{export_path}\\marker_projections.xml'
            
            project.chunk.exportMarkers(path=export_path, **kwargs)
            
            if export_format == 'both' and project.config.input.marker_reference.set_marker_manu == True:
                savepath_2    = os.path.normpath(project.config.input.marker_reference.exp_marker_path)
                # saveID        = project.project_dir.split('\\')[-2]
                filename      = os.path.basename(savepath_2).split('.')[0]
                dirname       = os.path.dirname(savepath_2)
                # export_path_2 = f'{savepath_2}\\{saveID}_marker_projections.xml' 
                export_path_2 = f'{dirname}\\{filename}.xml' 
                
                project.chunk.exportMarkers(path=export_path_2)

        # process logging and console output
        print('Metashape workflow: (OPT) exporting markers')
        project.logging(f'Export: marker in {export_format} format')

    def camera(project: object, **kwargs):

        '''
        Exports the positions of the point cloud and/or cameras from the active chunk.
        
        *args:
            project: your Metashape project\n
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportCameras
        '''

        format_  = kwargs.get('format', Metashape.ModelFormatOBJ)
        extens_  = str(format_).split('.')[-1].split('Format')[-1]
        
        savepath = f'{project.export_dir}\\{project.chunk.label}'        
        os.makedirs(savepath, exist_ok=True)        
        
        project.chunk.exportCameras(path=f'{savepath}\\cameras.{extens_.lower()}', **kwargs)

        # process logging and console output
        print('Metashape workflow: (OPT) exporting cameras')            
        project.logging(f'Export: cameras in {extens_} format')
            
    def tiled_model(project: object, pattern: str='', string: str='', **kwargs):
        
        '''
        Exports generated tiled model from the active chunk.
        
        NOTE for multiframe projects (e.g. class StereoProject): 
            exported file names are choosable from:
                - pattern: extracting a string from a time pattern in the source file name\n
                - string: using a given string by user plus image ID (0,1,...)\n
                - no pattern or string specified: using label of 1st camera per frame
                
        *args:
            project: your Metashape project\n
            pattern: re pattern for time stamp extraction from a filename\n
            string: designated filename for export
            
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportTiledModel
        '''

        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)
                    
        format_  = kwargs.get('format', Metashape.ModelFormatOBJ)       # dummy
        extens_  = str(format_).split('.')[-1].split('Format')[-1]                
                
        for i, frame in enumerate(project.chunk.frames):
            
            if project.stereo_RGB == True or project.stereo_IR == True:
                savepath_ = f'{savepath}\\tiled_models'
                os.makedirs(savepath, exist_ok=True)
                
                name     = frame.cameras[0].photo.path            
                if pattern != '' and string == '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}'
                elif pattern == '' and string != '':
                    savename = f'{savepath_}\\{string}_{i}'
                elif pattern != '' and string != '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}_{string}'
                else:
                    name     = os.path.basename(name).split('.')[0]
                    savename = f'{savepath_}\\{name}'
            else:
                savename = f'{savepath}\\tiled_model'            
            
            frame.exportTiledModel(path=f'{savename}.{extens_.lower()}', **kwargs)

        # process logging and console output
        print('Metashape workflow: (OPT) exporting tiled model')
        project.logging(f'Export: tiled model in {extens_} format')
        
    def model(project: object, pattern: str='', string: str='', **kwargs):
        
        '''
        Exports the generated 3D model for the active chunk.

        NOTE for multiframe projects (e.g. class StereoProject): 
            exported file names are choosable from:
                - pattern: extracting a string from a time pattern in the source file name\n
                - string: using a given string by user plus image ID (0,1,...)\n
                - no pattern or string specified: using label of 1st camera per frame
                
        *args:
            project: your Metashape project\n
            pattern: re.pattern for time stamp extraction from a filename\n
            string: designated filename for export
            
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportModel
        '''

        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)
        
        format_  = kwargs.get('format', Metashape.ModelFormatOBJ)       # dummy
        extens_  = str(format_).split('.')[-1].split('Format')[-1]
                
        for i, frame in enumerate(project.chunk.frames):
            
            if project.stereo_RGB == True or project.stereo_IR == True:
                savepath_ = f'{savepath}\\3DModels'
                os.makedirs(savepath, exist_ok=True)
                
                name     = frame.cameras[0].photo.path            
                if pattern != '' and string == '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}'
                elif pattern == '' and string != '':
                    savename = f'{savepath_}\\{string}'
                elif pattern != '' and string != '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}_{string}'
                else:
                    name     = os.path.basename(name).split('.')[0]
                    savename = f'{savepath_}\\{name}'
            else:
                savename = f'{savepath}\\3DModel'

            frame.exportModel(path=f'{savename}.{extens_.lower()}', **kwargs)
            
        # process logging and console output
        print('Metashape workflow: (OPT) exporting model')
        project.logging(f'Export: 3D model in {extens_} format')
        
    def raster(project: object, export_type: str, pattern: str='', string: str='', **kwargs):
        
        '''
        Exports the raster DEM or raster orthomosaic from the active chunk.

        NOTE for multiframe projects (e.g. class StereoProject): 
            exported file names are choosable from:
                - pattern: extracting a string from a time pattern in the source file name\n
                - string: using a given string by user plus image ID (0,1,...)\n
                - no pattern or string specified: using label of 1st camera per frame
                
        *args:
            project: your Metashape project\n
            export_type: used to classify the main type of exported raster in the filename\n
            pattern: re.pattern for time stamp extraction from a filename\n
            string: designated filename for export
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportRaster
        '''
        
        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)
        
        format_  = kwargs.get('format', Metashape.ImageFormatTIFF)      # dummy
        extens_  = str(format_).split('.')[-1].split('Format')[-1]
        
        # export raster to your export directory from each frame in a chunk
        for i, frame in enumerate(project.chunk.frames):

            if project.stereo_RGB == True or project.stereo_IR == True:
                savepath_ = f'{savepath}\\raster'
                os.makedirs(savepath, exist_ok=True)
                
                name     = frame.cameras[0].photo.path            
                if pattern != '' and string == '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{export_type}_{name[0]}'
                elif pattern == '' and string != '':
                    savename = f'{savepath_}\\{export_type}_{string}'
                elif pattern != '' and string != '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}_{string}'
                else:
                    name     = os.path.basename(name).split('.')[0]
                    savename = f'{savepath_}\\{name}'
            else:
                savename = f'{savepath}\\{export_type}'

            frame.exportRaster(path=f'{savename}.{extens_.lower()}', **kwargs)

        # process logging and console output
        print(f'Metashape workflow: (OPT) exporting raster in {extens_} format')
        project.logging(f'Export: raster as {export_type} in {extens_} format')
    
    def report(project: object, **kwargs):
        
        ''' 
        Exports the processing report in PDF-format.
        
        *args: 
            project: your Metashape project\n
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportReport
        '''
        
        # export report to your export directory
        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)
        
        project.chunk.exportReport(path=f'{savepath}\\report.pdf', **kwargs)
        
        # process logging and console output
        print('Metashape workflow: (OPT) exporting report')
        project.logging('Export: processing report in PDF format')
        
    def point_cloud(project: object, pattern: str='', string: str='', **kwargs):
        
        ''' 
        Exports the point cloud from the active chunk.
        
        NOTE for multiframe projects (e.g. class StereoProject): 
            exported file names are choosable from:
                - pattern: extracting a string from a time pattern in the source file name\n
                - string: using a given string by user plus image ID (0,1,...)\n
                - no pattern or string specified: using label of 1st camera per frame
                
        *args:
            project: your Metashape project\n
            pattern: re.pattern for time stamp extraction from a filename\n
            string: designated filename for export
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.exportPointCloud
        '''       

        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)

        format_  = kwargs.get('format', Metashape.PointCloudFormatOBJ)      # dummy
        extens_  = str(format_).split('.')[-1].split('Format')[-1]
        
        for i, frame in enumerate(project.chunk.frames):
            
            if project.stereo_RGB == True or project.stereo_IR == True:
                savepath_ = f'{savepath}\\point_clouds'
                os.makedirs(savepath, exist_ok=True)
                
                name     = frame.cameras[0].photo.path            
                if pattern != '' and string == '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}'
                elif pattern == '' and string != '':
                    name     = string
                    savename = f'{savepath_}\\{name}'
                elif pattern != '' and string != '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}_{string}'
                else:
                    name     = os.path.basename(name).split('.')[0]
                    savename = f'{savepath_}\\{name}'
            else:
                savename = f'{savepath}\\point_cloud'
                
            if str(Metashape.version)[0] == '1':
                frame.exportPoints(path=f'{savename}.{extens_.lower()}', **kwargs)        
            if str(Metashape.version)[0] == '2': 
                frame.exportPointCloud(path=f'{savename}.{extens_.lower()}', **kwargs)

        # process logging and console output
        print('Metashape workflow: (OPT) exporting point cloud')                
        project.logging(f'Export: point cloud in {extens_} format')

    def precision_map(project: object, pattern: str='', string: str='', export_format: str='txt', **kwargs):

        '''
        Exports the presicion map as text file from the active chunk.
        
        This functionality is based on James et al (2017) - 
        3-D uncertainty-based topographic change detection with structure-from-motion photogrammetry: 
        precision maps for ground control and directly georeferenced surveys, Earth Surf. Proc. Landforms
        
        --> visit http://tinyurl.com/sfmgeoref for more information.
        
        NOTE for multiframe projects (e.g. class StereoProject): 
            exported file names are choosable from:
                - pattern: extracting a string from a time pattern in the source file name\n
                - string: using a given string by user plus image ID (0,1,...)\n
                - no pattern or string specified: using label of 1st camera per frame

        *args:
            project: your Metashape project\n
            pattern: re.pattern for time stamp extraction from a filename\n
            string: designated filename for export\n
            export_format: export text file format
        '''


        savepath = f'{project.export_dir}\\{project.chunk.label}'
        os.makedirs(savepath, exist_ok=True)

        extens_  = export_format

        # transform coordinate system to local coordinates
        # NOTE: region will be reseted to default - was nicht stimmt
        M = project.chunk.transform.matrix
        s = project.chunk.transform.scale
        m = project.chunk.crs.localframe(M.mulp(project.chunk.region.center))
        
        T = m * M
        
        if s:
            R = s * T.rotation()
        else:
            R = T.rotation()
    
        for i, frame in enumerate(project.chunk.frames):
            
            if project.stereo_RGB == True or project.stereo_IR == True:
                savepath_ = f'{savepath}\\precision_maps'
                os.makedirs(savepath_, exist_ok=True)
                
                name     = frame.cameras[0].photo.path            
                if pattern != '' and string == '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}'
                elif pattern == '' and string != '':
                    name     = string
                    savename = f'{savepath_}\\{name}'
                elif pattern != '' and string != '':
                    name     = hlp.extract_date_stamps([name], pattern=pattern)
                    savename = f'{savepath_}\\{name[0]}_{string}'
                else:
                    name     = os.path.basename(name).split('.')[0]
                    savename = f'{savepath_}\\{name}'

            else:
                savename = f'{savepath}\\precision_map'
                
            with open(f'{savename}.{extens_.lower()}', 'w') as fid:
                # define a writer generator and line parameters
                fwriter = csv.writer(fid, delimiter='\t', lineterminator='\n')
                # write header into file
                fwriter.writerow(['X(m)', 'Y(m)', 'Z(m)', 
                                  'sX(mm)', 'sY(mm)', 'sZ(mm)', 
                                  'covXX(m2)', 'covXY(m2)', 'covXZ(m2)', 
                                  'covYY(m2)', 'covYZ(m2)', 'covZZ(m2)'])
                
                # iterate through the tie point cloud      
                for j, point in enumerate(frame.tie_points.points):
            
                    # check if the point is usable
                    if not point.valid: continue
                
                    # transform point coordinates into output coordinate system
                    if project.chunk.crs: 
                        V = M * (point.coord)
                        V.size = 3
                        pt_coord = project.chunk.crs.project(V)
                    
                    # transform point covariance matrix into output coordinate system
                    pt_covars = R * point.cov * R.t()
            
                    # write into the output file
                    fwriter.writerow([
                        '{0:0.5f}'.format(pt_coord[0]), 
                        '{0:0.5f}'.format(pt_coord[1]), 
                        '{0:0.5f}'.format(pt_coord[2]),
                        '{0:0.7f}'.format(math.sqrt(pt_covars[0, 0]) * 1000),
                        '{0:0.7f}'.format(math.sqrt(pt_covars[1, 1]) * 1000),
                        '{0:0.7f}'.format(math.sqrt(pt_covars[2, 2]) * 1000),
                        '{0:0.9f}'.format(pt_covars[0, 0]), 
                        '{0:0.9f}'.format(pt_covars[0, 1]),
                        '{0:0.9f}'.format(pt_covars[0, 2]),
                        '{0:0.9f}'.format(pt_covars[1, 1]), 
                        '{0:0.9f}'.format(pt_covars[1, 2]),
                        '{0:0.9f}'.format(pt_covars[2, 2])])

        # process logging and console output       
        print('Metashape workflow: (OPT) exporting precision map')                
        project.logging(f'Export: precision map in {extens_.upper()} format')

###############################################################################
# Point cloud and tie point cloud

class PointCloud():
    
    class Classification():
        
        def classify_point_cloud(project:      object,
                                 class_param:  tuple,
                                 save_project: tuple = (False, ''),
                                 **kwargs):
    
            '''
            Classifies the point cloud in an active chunk into ground and non-ground classes.
            
            *args:
                project: your Metashape project\n
                class_param: (boolean, type, paramset)
                        type: 'test', 'vine', 'crop'\n
                        paramset if type is not 'test': 'set1', 'set2', ...\n
                        paramset if type is 'test': {'max_angle': float, 'max_distance': float, 'cell_size': float}
                save_project: (True/False, active_chunk.label)
    
            **kwargs:
                Get further information in the user manual:\n
                https://www.agisoft.com/downloads/user-manuals/\n\n
                --> class Metashape.PointCloud.classifyGroundPoints
    
            Returns:
                Updated Metashape project
            '''
            
            # time tracking
            start_time = time.time()
                
            # get keyword arguments from class_param list
            parameterset = ppp.classPM(paramSet=class_param[1:])
            max_angle    = getattr(parameterset.Classification, class_param[1]).max_angle
            max_dist     = getattr(parameterset.Classification, class_param[1]).max_dist
            cell_size    = getattr(parameterset.Classification, class_param[1]).cell_size
    
            # process logging and console output      
            print('Metashape workflow: (OPT) classifying point cloud')
            
            arguments = {'max_angle': max_angle, 'max_distance': max_dist, 'cell_size': cell_size}    
            for key, value in kwargs.items():        
                arguments[key] = value
            arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])
            
            project.logging(f'Point cloud classification into ground and non-ground classes:\n{arguments_string}')
    
            # ensure, that argument project is an instance of _MetashapeProject-class    
            if not isinstance(project, _MetashapeProject):
                raise TypeError('The passed project-object needs to be inheritted from _MetashapeProject class.'
                                'Like the MultispectralProject or RGBProject classes.')
    
            # point cloud classification
            # since Metashape version 2.0.0 dense_cloud was renamed to point_cloud.
            if str(Metashape.version)[0] == '1':
                project.chunk.dense_cloud.classifyGroundPoints(max_angle=max_angle, max_distance=max_dist, 
                                                               cell_size=cell_size, **kwargs)
            if str(Metashape.version)[0] == '2':
                project.chunk.point_cloud.classifyGroundPoints(max_angle=max_angle, max_distance=max_dist,
                                                               cell_size=cell_size, **kwargs)
    
            hlp.log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS')
                
            # save project and redefine the working chunk
            if save_project[0] == True:            
                project.saveMetashapeProject(active_chunk=save_project[1])
    
            return project

        def prepare_classification(project:     object, 
                                   config_data: dict):
            
            '''
            Extracts classification specifications from the configuration file 
            and, if specified, generates a new chunk dedicated to point cloud classification.
            
            *args:
                project: your Metashape project\n
                config_data: content of the project configuration file
            
            Returns:
                Updated Metashape project, and a tuple containing the specifications for classification
            '''
            
            class_usage = config_data['metashape']['point_cloud']['classification']['use']
            new_chunk   = config_data['metashape']['point_cloud']['classification']['copy_chunk']
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
            
            if new_chunk == True and class_usage == True:
                project.chunk.copy()
                
                if classPC[1] == 'test': chunk_name = f'classified_{classPC[1]}'
                else:                    chunk_name = f'classified_{classPC[1]}_{classPC[2]}'
                
                project.doc.chunks[-1].label = chunk_name
            
            if new_chunk == False and class_usage == True:
                old_label = project.chunk.label
                
                if classPC[1] == 'test': chunk_name = f'{old_label}_classified_{classPC[1]}'
                else:                    chunk_name = f'{old_label}_classified_{classPC[1]}_{classPC[2]}'
                
                project.doc.chunks[project.chunk_ID].label = chunk_name

            return project, classPC
            

    class Filter():
        
        def filter_from_list(project:           object,
                             filter_unclass:    bool  = False,
                             filter_high_noise: bool  = False,
                             filter_ground:     bool  = False,
                             render_preview:    bool  = False,
                             save_project:      tuple = (False, '')):
            
            '''
            Function that simultaneously calls several filter options controlled by Boolean flags.
        
            *args:
                project: your Metashape project\n
                filter_unclass: [True/False]\n
                filter_high_noise: [True/False]\n
                filter_ground: [True/False]\n
                render_preview: [True/False]\n
                save_project: (True/False, active_chunk.label)

            Returns:
                Updated Metashape project
            '''
    
            if filter_unclass == True:
                project = ppp.PointCloud.Filter.delete_point_class(project        = project,
                                                                   point_class    = Metashape.PointClass.Unclassified,
                                                                   render_preview = (render_preview, 'classifiedPC_unclassifiedPointsFilter'),
                                                                   save_project   = save_project)
                
            if filter_high_noise == True:
                project = ppp.PointCloud.Filter.delete_point_class(project        = project,
                                                                   point_class    = Metashape.PointClass.HighNoise,
                                                                   render_preview = (render_preview, 'classifiedPC_highNoiseFilter'),
                                                                   save_project   = save_project)
                    
            if filter_ground == True:
                project = ppp.PointCloud.Filter.delete_point_class(project        = project,
                                                                   point_class    = Metashape.PointClass.Ground,
                                                                   render_preview = (render_preview, 'classifiedPC_groundPointFilter'),
                                                                   save_project   = save_project)
                
            return project    

        def delete_point_class(project:        object,
                               point_class:    object = Metashape.PointClass.Ground,
                               render_preview: tuple  = (False, ''),
                               save_project:   tuple  = (False, '')):

            '''
            Removes a given point class from classified point cloud.
            
            *args:
                project: your Metashape project\n
                render_preview: [True/False]\n
                save_project: (True/False, active_chunk.label)
                
                point_class: 
                    Get further information in the user manual:\n
                    https://www.agisoft.com/downloads/user-manuals/\n\n
                    --> class Metashape.PointClass
                    
            Returns:
                Updated Metashape project
            '''
            
            chunk = project.chunk.label           
            os.makedirs(f'{project.export_dir}\\{chunk}', exist_ok=True)
            
            _class = str(point_class).split('.')[-1].lower()
            
            if str(Metashape.version)[0] == '1':
                project.chunk.dense_cloud.removePoints([Metashape.PointClass.Ground])
                project.logging(f'Removing PointClass: {point_class}')
                if render_preview[0] == True:
                    project.chunk.dense_cloud.renderPreview().save(path=f'{project.export_dir}/{chunk}/{render_preview[1]}.tiff')
                    
            if str(Metashape.version)[0] == '2':
                project.chunk.point_cloud.removePoints([Metashape.PointClass.Ground])
                project.logging(f'Removing PointClass: {point_class}')
                if render_preview[0] == True:
                    project.chunk.point_cloud.renderPreview().save(path=f'{project.export_dir}/{chunk}/{render_preview[1]}.tiff')

            # process logging and console output
            print(f'Metashape workflow: (OPT) filtering point cloud for {_class} points')
            project.logging(f'Filtering point cloud for: {_class} points')
            
            # save project and redefine the working chunk
            if save_project[0] == True:            
                project.saveMetashapeProject(active_chunk=save_project[1])
            
            return project


class TiePointCloud():
    
    class Filter():
        
        def return_minmax(project:   object,
                          criterion: object):
            
            '''
            Calculates the minimum and maximum values of a tie point cloud based on the specified criterion.
            
            *args:
                project: your Metashape project\n
                criterion:
                    Get further information in the user manual:\n
                    https://www.agisoft.com/downloads/user-manuals/\n
                    --> class Metashape.TiePoints.Filter.Criterion
            
            Returns:
                min, max
            '''
            
            if str(Metashape.version)[0] == '1':
                f = Metashape.PointCloud.Filter()
            if str(Metashape.version)[0] == '2':
                f = Metashape.TiePoints.Filter()
                
            f.init(project.chunk, criterion=criterion)
            
            return f.min_value, f.max_value


        def gradual_selection(project:      object,
                              criterion:    object,
                              threshold:    float,
                              save_project: tuple = (False, '')):
            
            '''
            Selects points from a tie point cloud based on a threshold for the specified criterion.
            
            *args:
                project: your Metashape project\n
                criterion:
                    Get further information in the user manual:\n
                    https://www.agisoft.com/downloads/user-manuals/\n
                    --> class Metashape.TiePoints.Filter.Criterion
                threshold: threshold used for tie point selection
                save_project: (True/False, active_chunk.label)
            
            Returns:
                Updated Metashape project
            '''
            
            # process logging and console output      
            print('Metashape workflow: (OPT) filter tie point cloud; select')
            project.logging(f'Tie points: selected by criterion {criterion}')

            if str(Metashape.version)[0] == '1':
                f = Metashape.PointCloud.Filter()
            if str(Metashape.version)[0] == '2':
                f = Metashape.TiePoints.Filter()

            f.init(project.chunk, criterion=criterion)
            f.selectPoints(threshold)

            if save_project[0] == True:
                project.saveMetashapeProject(active_chunk=save_project[1])
                
            return project


        def gradual_removal(project:          object,
                            criterion:        object,
                            threshold:        float,
                            save_project:     tuple = (False, '')):
            
            '''
            Removes points from a tie point cloud based on a threshold for the specified criterion.
            
            *args:
                project: your Metashape project\n
                criterion:
                    Get further information in the user manual:\n
                    https://www.agisoft.com/downloads/user-manuals/\n
                    --> class Metashape.TiePoints.Filter.Criterion
                threshold: threshold used for tie point selection\n
                save_project: (True/False, active_chunk.label)
            
            Returns:
                Updated Metashape project
            '''
            
            # process logging and console output      
            print('Metashape workflow: (OPT) filter tie point cloud; remove')
            project.logging(f'Tie points: removed by criterion {criterion}')

            if str(Metashape.version)[0] == '1':
                f = Metashape.PointCloud.Filter()
            if str(Metashape.version)[0] == '2':
                f = Metashape.TiePoints.Filter()

            f.init(project.chunk, criterion=criterion)
            f.removePoints(threshold)

            if save_project[0] == True:
                project.saveMetashapeProject(active_chunk=save_project[1])
            
            return project


###############################################################################
# Bounding Box

class BBox():
    
    def return_rot_matrix(project:     object,
                          return_type: type = Metashape.Matrix):
        
        '''
        Returns the rotation matrix of the region in the active chunk.
        
        *args:
            project: your Metashape project\n
            return_type: [Metashape.Matrix, list] - rot matrix return type
            
        Returns:
            (a) Metashape.Matrix object (default)\n 
            (b) or list: [[M_00, M_01, M_02],[M_10, M_11, M_12],[M_20, M_21, M_22]]
        '''
        
        M = [[project.chunk.region.rot[0,0], project.chunk.region.rot[0,1], project.chunk.region.rot[0,2]],
             [project.chunk.region.rot[1,0], project.chunk.region.rot[1,1], project.chunk.region.rot[1,2]],
             [project.chunk.region.rot[2,0], project.chunk.region.rot[2,1], project.chunk.region.rot[2,2]]]
        
        if return_type == Metashape.Matrix:
            return project.chunk.region.rot
        
        if return_type == list:
            return M
    
    def rotate_region(project:      object,
                      input_matrix: object,
                      input_type:   type  = Metashape.Matrix,
                      save_project: tuple = (False, '')):
    
        '''
        Updates the rotation matrix values of the region in the active chunk.
        
        *args:
            project: your Metashape project\n
            input_matrix: 3x3 matrix to set as new rotation matrix\n
            input_type: [Metashape.Matrix, list] - format of 3x3 input matrix \n
            save_project: (True/False, active_chunk.label) 
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output            
        print('Metashape workflow: (OPT) rotate region for analysis')
        project.logging('Bounding Box: rotation matrix updated')
        
        if input_type == Metashape.Matrix:
            project.chunk.region.rot = input_matrix
        
        if input_type == list:
            project.chunk.region.rot = Metashape.Matrix(input_matrix)

        # save project and redefine the working chunk   
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
                
        return project
            
    def return_xyz_extent(project:     object,
                          return_type: type = Metashape.Vector):

        '''
        Returns the extent of the region in the active chunk.
        
        *args:
            project: your Metashape project\n
            return_type: [Metashape.Vector, tuple] - xyz vector return type
        
        Returns:
            (a) Metashape.Vector object (default)\n 
            (b) tuple: (x,y,z)
        '''
        
        if return_type == Metashape.Vector:
            return project.chunk.region.size
        
        if return_type == tuple:
            return tuple(project.chunk.region.size)
        
    def resize_xyz_extent(project:      object,
                          xyz_extent:   tuple,
                          xyz_type:     str   = Metashape.Vector,
                          save_project: tuple = (False, '')):

        '''
        Resizes the region by a given set of values.
        
        *args:
            project: your Metashape project\n
            xyz_extent: xyz vector to set as the new extent\n
            xyz_type: [Metashape.Vector, tuple] - xyz vector format\n
            save_project: (True/False, active_chunk.label)

        Returns:
            Updated Metashape project
        '''

        # process logging and console output            
        print('Metashape workflow: (OPT) resize region for analysis')
        project.logging(f'Bounding Box: resized to {xyz_extent}')
        
        if xyz_type == Metashape.Vector:
            project.chunk.region.size = xyz_extent
        
        if xyz_type == tuple:
            project.chunk.region.size = Metashape.Vector(xyz_extent)

        # save project and redefine the working chunk   
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
            
        return project

    
    def return_center(project:     object,
                      return_type: type = Metashape.Vector):

        '''
        Returns the center of the region in the active chunk.
        
        *args:
            project: your Metashape project\n
            return_type: [Metashape.Vector, tuple] - xyz vector return type
        
        Returns:
            (a) Metashape.Vector object (default)\n 
            (b) tuple: (x,y,z)
        '''
        
        if return_type == Metashape.Vector:
            return project.chunk.region.center
        
        if return_type == tuple:
            return tuple(project.chunk.region.center)        
        
    def redefine_center(project:      object,
                        xyz_coord:    tuple,
                        xyz_type:     str   = Metashape.Vector,
                        save_project: tuple = (False, '')):

        '''
        Moves the region center in the active chunk.
        
        *args:
            project: your Metashape project\n
            xyz_coord: xyz vector to set as the new region center\n
            xyz_type: [Metashape.Vector, tuple] - xyz vector format\n
            save_project: (True/False, active_chunk.label)

        Returns:
            Updated Metashape project
        '''

        # process logging and console output            
        print('Metashape workflow: (OPT) redefine center of region')
        project.logging(f'Bounding Box: center moved to {xyz_coord}')
        
        # change center of bounding box
        if xyz_type == Metashape.Vector:
            project.chunk.region.center = xyz_coord
        
        if xyz_type == tuple:
            project.chunk.region.center = Metashape.Vector(xyz_coord)

        # save project and redefine the working chunk   
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
            
        return project

    def redefine_auto_multiframe(project:      object,
                                 reference_ID: int   = 0,
                                 save_project: tuple = (False, '')):
        
        '''
        Resizes the bounding box in a multiframe project based on the maximum extent
        in the x, y, or z direction from the different frame tie point clouds.
        The center of the region is moved to match to the center of the image defined by the reference ID.
        
        *args:
            project: your Metashape project\n
            reference_ID: ID of the reference frame\n
            save_project: (True/False, active_chunk.label)

        Returns:
            Updated Metashape project
        '''

        # process logging and console output            
        print('Metashape workflow: (OPT) redefine region for analysis (auto)')
        project.logging('Bounding Box: automatically redefined')
        
        # resize BBox
        ID = reference_ID
        
        regionSize   = {'x':[], 'y':[], 'z':[]}
        regionCenter = {'x':[], 'y':[], 'z':[]}
                
        for j, frame in enumerate(project.chunk.frames):
            
            for i, p in enumerate(frame.tie_points.points):
                if i==0: 
                    a = {'x':[], 'y':[], 'z':[]}
                
                a['x'].append(p.coord[0])
                a['y'].append(p.coord[1])
                a['z'].append(p.coord[2])
            
                if i == len(frame.tie_points.points)-1:
                    x1 = np.mean([np.min(a['x']),np.max(a['x'])])                    
                    x2 = np.abs(np.min(a['x']))+np.abs(np.max(a['x']))                    
                    y1 = np.mean([np.min(a['y']),np.max(a['y'])])                    
                    y2 = np.abs(np.min(a['y']))+np.abs(np.max(a['y']))                    
                    z1 = np.mean([np.min(a['z']),np.max(a['z'])])                    
                    z2 = np.abs(np.diff((np.min(a['z']),np.max(a['z']))))
                    
                    regionCenter['x'].append(x1)
                    regionCenter['y'].append(y1)
                    regionCenter['z'].append(z1)
                    
                    regionSize['x'].append(x2)
                    regionSize['y'].append(y2)
                    regionSize['z'].append(z2)
        
        project.chunk.region.center = Metashape.Vector((regionCenter['x'][ID],
                                                        regionCenter['y'][ID],
                                                        regionCenter['z'][ID] + np.max(regionSize['z'])/2))

        project.chunk.region.size   = Metashape.Vector((np.max(regionSize['x'])+np.max(regionSize['x'])/2,
                                                        np.max(regionSize['y'])+np.max(regionSize['y'])/2,
                                                        np.max(regionSize['z'])+np.max(regionSize['z'])/2))                    

        # save project and redefine the working chunk   
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])

        return project        


###############################################################################
# REFERENCES

class Reference():

    def set_marker_manually(project:      object,
                            config_data:  dict,
                            save_project: tuple = (False, '')):
        
        '''
        Pauses execution to add marker flags manually in the Metashape GUI. 
        Ensure all markers are set with green flags.\n
        Note: Save your project in the GUI when done!

        *args:
            project: your Metashape project\n
            config_data: content of the project configuration file\n
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output            
        print('Metashape workflow: (OPT) adding markers manually')
        project.logging('Markers: manually set')
        
        # manually set and then enable markers + re-open the existing project
        active_chunk = [a.label for a in project.doc.chunks].index(save_project[1])

        if config_data['metashape']['document']['read_only'] == True:
            ask = input('\nSaving is disabled in read-only mode. Change to editing mode [y,n]?: ')
            
            if ask == 'y':
                config_data['metashape']['document']['read_only'] = False
            if ask == 'n':
                print('\n--> No markers were added to your project.')
                return project
            
        project.doc.clear()
        config_data['input']['general']['new_project'] = False
        config_data['metashape']['chunk']['ID_active'] = active_chunk
        config_file = f'{project.project_ID}.yaml' # for creating the right project ID
        
        input('\nPlease use Metashape GUI to add markers to your project!\n'
              'For an example, take a look into to the PyExpress-Tutorial.\n'
              'Finally, save your project! Then, please press [enter] when you have finished.')
        
        project = ppp.DroneProject(config_data = config_data,
                                   project_dir = project.project_dir, 
                                   image_dir   = project.image_dir,
                                   config_name = config_file)
        
        project.chunk = project.doc.chunks[active_chunk]

        for marker in project.chunk.markers:
            marker.Reference.enabled = True
            
        project.chunk.marker_crs = project.chunk.world_crs

        ppp.Export.marker(project, export_format='both')

        # save project and redefine the working chunk      
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])

        return project
    
    def import_marker_proj(project:      object,
                           coord_system: object,
                           optimize_cam: bool  = False,
                           save_project: tuple = (False, '')):
        
        '''
        Imports marker projections into an active chunk in either CSV or XML format.
        
        *args:
            project: your Metashape project\n
            coord_system: marker coordinate sytem - ['local', 'EPSG::']; e.g. "EPSG::4326"\n
                --> EPSG code refers to class Metashape.CoordinateSystem
            optimize_cam: apply camera optimization using default values\n
                --> refers to class Metashape.Chunk.optimizeCameras
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output          
        print('Metashape workflow: (OPT) adding GCP occurence in images (projections)')
        project.logging('Markers: marker to image projections imported')
        
        # import marker projections based on file type
        file_type       = os.path.splitext(os.path.basename(project.marker_proj_path))[1].lower()
        
        if file_type == '.csv':
            marker_list  = pd.read_csv(project.marker_proj_path, sep=',', 
                                       on_bad_lines='skip', low_memory=False,
                                       names=['GCP','IMG','x_proj','y_proj'])
    
            for ind, row in marker_list.iterrows():            
                GCPLabel = row['GCP']            
                camLabel = row['IMG']
                x, y     = row['x_proj'], row['y_proj']
                if not camLabel in [c.label for c in project.chunk.cameras]:
                    continue
                if GCPLabel in [m.label for m in project.chunk.markers]:
                    markerIndex   = [a.label for a in project.chunk.markers].index(GCPLabel)
                    _marker       = project.chunk.markers[markerIndex]
                if not GCPLabel in [m.label for m in project.chunk.markers]:
                    _marker       = project.chunk.addMarker()
                    _marker.label = GCPLabel
                if camLabel in [c.label for c in project.chunk.cameras]:
                    camIndex      = [a.label for a in project.chunk.cameras].index(camLabel)
                    camera        = project.chunk.cameras[camIndex]
                    _pixelCoords  = Metashape.Marker.Projection(Metashape.Vector([x,y]), True)
                    _marker.projections[camera]        = _pixelCoords
                    _marker.projections[camera].pinned = True  
        
        if file_type == '.xml':
            project.chunk.importMarkers(path=project.marker_proj_path)
        
        if coord_system == 'local':
            project.chunk.marker_crs = 'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
        else:
            project.chunk.marker_crs = Metashape.CoordinateSystem(coord_system)

        # optional camera optimization        
        if optimize_cam == True:
            project = ppp.Reference.optimize_cameras(project=project)

        # save project and redefine the working chunk           
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
        
        return project

    def import_marker_coord(project:      object,
                            coord_system: object,
                            optimize_cam: bool  = False,
                            save_project: tuple = (False, ''),
                            **kwargs):

        '''
        Imports a list of measured real-world coordinates for ground control points into the active chunk.
        
        *args:
            project: your Metashape project\n
            coord_system: marker coordinate sytem - ['local', 'EPSG::']; e.g. "EPSG::4326"\n
                --> EPSG code refers to class Metashape.CoordinateSystem
            optimize_cam: apply camera optimization using default values\n
                --> refers to class Metashape.Chunk.optimizeCameras
            save_project: (True/False, active_chunk.label)
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.importReference
                
        Returns:
            Updated Metashape project
        '''

        # process logging and console output      
        print('Metashape workflow: (OPT) adding ground control points to chunk')
        project.logging('Markers: real-world coordinates imported')
        
        # import and enable markers
        project.chunk.importReference(**kwargs)
        
        for marker in project.chunk.markers:
            marker.Reference.enabled = True

        if coord_system == 'local':
            project.chunk.marker_crs = 'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
        else:
            project.chunk.marker_crs = Metashape.CoordinateSystem(coord_system)

        # optional camera optimization        
        if optimize_cam == True:
            project = ppp.Reference.optimize_cameras(project=project)

        # save project and redefine the working chunk           
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
        
        return project

    def add_scalebar(project:      object,
                     distance:     float,
                     accuracy:     float,
                     enable:       bool,
                     image_IDs:    list  = [0,1],
                     optimize_cam: bool  = False,
                     save_project: tuple = (False, '')):

        '''
        Defines a scalebar between two images of your image set in the active chunk.
        
        *args:
            project: your Metashape project\n
            distance: distance between a given start- and an endpoint in meters\n
            accuracy: accuracy of the distance/scalebar in meters\n
            enable: enables/disables the scalebar\n
            camera_IDs: IDs of the images between which a scalebar will be defined\n
            optimize_cam: apply camera optimization using default values\n
                --> refers to class Metashape.Chunk.optimizeCameras
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output           
        print('Metashape workflow: (OPT) setting scalebar')
        
        item_list = [['distance', distance], ['accuracy', accuracy], ['image_IDs', image_IDs]]
        arguments_string = '\n'.join([f'    {key}: {value}' for key, value in item_list])
        
        project.logging(f'Scalebar added to active chunk:\n{arguments_string}')
        
        # set scalebar and accuracy parameters
        scalebar = project.chunk.addScalebar(project.chunk.cameras[image_IDs[0]], 
                                             project.chunk.cameras[image_IDs[1]])

        scalebar.reference.distance = distance
        scalebar.reference.accuracy = accuracy
        scalebar.reference.enabled  = enable

        # optional camera optimization
        if optimize_cam == True:
            project = ppp.Reference.optimize_cameras(project=project)

        # save project and redefine the working chunk   
        if save_project[0] == True:
            project.saveMetashapeProject(active_chunk=save_project[1])
            
        return project

    def set_reference_param(project:      object,
                            config_data:  dict,
                            optimize_cam: bool  = False,
                            save_project: tuple = (False, '')):

        '''
        Sets reference parameters corresponding to the Reference Settings block in the Metashape GUI
        and based on configuration file specifications.
       
        *args:
            project: your Metashape project\n
            config_data: content of the project configuration file\n
            optimize_cam: apply camera optimization using default values\n
                --> refers to class Metashape.Chunk.optimizeCameras
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project        
        '''

        # process logging and console output   
        print('Metashape workflow: (OPT) setting reference parameters')
        project.logging('Reference parameters set')
        
        # general references
        chunk_crs         = config_data['metashape']['reference']['general']['chunk_crs']
        
        camera_crs        = config_data['metashape']['reference']['measurement']['camera_crs']
        camera_acc_met    = config_data['metashape']['reference']['measurement']['camera_acc_met']
        camera_acc_deg    = config_data['metashape']['reference']['measurement']['camera_acc_deg']
        
        marker_crs        = config_data['metashape']['reference']['measurement']['marker_crs']
        marker_acc        = config_data['metashape']['reference']['measurement']['marker_acc']
        
        marker_acc_img    = config_data['metashape']['reference']['projection']['marker_acc']
        tiepoint_acc_img  = config_data['metashape']['reference']['projection']['tiepoint_acc']
        
        scalebar_acc      = config_data['metashape']['reference']['scalebar']['acc']
        
        local_crs         = 'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
        
        # set reference coordinate systems
        if chunk_crs == 'local':
            project.chunk.crs        = Metashape.CoordinateSystem(local_crs)
        else:
            project.chunk.crs        = Metashape.CoordinateSystem(chunk_crs)
        
        if camera_crs == 'local':
            project.chunk.camera_crs = Metashape.CoordinateSystem(local_crs)
        else:
            project.chunk.camera_crs = Metashape.CoordinateSystem(camera_crs)
        
        if marker_crs == 'local':
            project.chunk.marker_crs = Metashape.CoordinateSystem(local_crs)
        else:
            project.chunk.marker_crs = Metashape.CoordinateSystem(marker_crs)

        # set reference accuracies
        project.chunk.marker_location_accuracy   = Metashape.Vector(marker_acc)
        project.chunk.marker_projection_accuracy = marker_acc_img
        project.chunk.tiepoint_accuracy          = tiepoint_acc_img
        project.chunk.camera_location_accuracy   = Metashape.Vector(camera_acc_met)
        project.chunk.camera_rotation_accuracy   = Metashape.Vector(camera_acc_deg)
        project.chunk.scalebar_accuracy          = scalebar_acc

        # optional camera optimization
        if optimize_cam == True:
            project = ppp.Reference.optimize_cameras(project=project)

        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])
           
        return project

    def set_camera_param(project:      object,
                         config_data:  dict,
                         optimize_cam: bool  = False,
                         save_project: tuple = (False, '')):
        
        '''
        Sets camera position and accuracy parameters based on configuration file specifications.
        Designed for projects with fixed camera installations, e.g. stereo camera projects.
       
        *args:
            project: your Metashape project\n
            config_data: content of the project configuration file\n
            optimize_cam: apply camera optimization using default values\n
                --> refers to class Metashape.Chunk.optimizeCameras
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output   
        print('Metashape workflow: (OPT) setting camera/image locations')
        project.logging('Camera/image locations set')
        
        # set image location and accuracy parameters
        for i, cam in enumerate(project.chunk.cameras):
            spec = config_data['metashape']['setup'][f'sensor{i+1}']['reference']

            if spec['use'] == True:
                cam.reference.location          = Metashape.Vector(spec['loc'])
                cam.reference.location_accuracy = Metashape.Vector(spec['acc'])

        # optional camera optimization
        if optimize_cam == True:
            project = ppp.Reference.optimize_cameras(project=project)

        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])
           
        return project

    def optimize_cameras(project:          object,
                         update_transform: bool  = True,
                         save_project:     tuple = (False, ''),
                         **kwargs):

        '''
        Performs optimization of tie points / camera parameters.
        
        *args:
            project: your Metashape project\n
            update_transform: update chunk transformation before optimizing cameras\n
            save_project: (True/False, active_chunk.label) 
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Chunk.optimizeCameras
 
        Returns:
            Updated Metashape project 
        '''
        
        # chunk transformation and camera optimization
        if update_transform == True:
            project = ppp.Reference.update_transform(project=project)

        project.chunk.optimizeCameras(**kwargs)

        # process logging and console output        
        print('Metashape workflow: (OPT) optimizing camera/tiepoint parameters')

        arguments = dict()        
        for key, value in kwargs.items():        
            arguments[key] = value
        arguments_string = '\n'.join([f'    {key}: {value}' for key, value in arguments.items()])        
        if not arguments_string: arguments_string = '    default settings'
        
        project.logging(f'Cameras optimized:\n{arguments_string}')
                
        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])

        return project        

    def update_transform(project:      object,
                         save_project: tuple = (False, '')):

        '''
        Updates chunk transformation based on reference data.
        
        *args:
            project: your Metashape project\n
            save_project: (True/False, active_chunk.label)

        Returns:
            Updated Metashape project            
        '''
        
        # process logging and console output
        print('Metashape workflow: (OPT) updating chunk transformation')
        project.logging('Updated chunk transformation')
        
        # chunk transformation based on reference data
        project.chunk.updateTransform()
        
        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])
           
        return project

###############################################################################
# CAMERA CALIBRATION

class Calibration():
    
    def import_from_file(project:      object,
                         save_project: tuple = (False, ''), 
                         **kwargs):
        
        '''
        Imports lens calibration values from a specified calibration file.
        
        *args:
            project: your Metashape project\n
            save_project: (True/False, active_chunk.label)
        
        **kwargs:
            Get further information in the user manual:\n
            https://www.agisoft.com/downloads/user-manuals/\n\n
            --> class Metashape.Calibration.load
        
        Returns:
            Updated Metashape project
        '''

        # process logging and console output
        print('Metashape workflow: (OPT) loading sensor parameters from file')
        project.logging('Calibration: sensor calibration loaded from file')
        
        # calibration of single sensor by file content
        sensor            = project.chunk.sensors[0]
        cal               = Metashape.Calibration()        
        cal.load(**kwargs) 
        sensor.user_calib = cal
        sensor.fixed      = True
        
        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])

        return project

    def set_sensor_param_stereo(project:      object,
                                config_data:  dict,
                                save_project: tuple = (False, '')):
        
        '''
        Sets sensor attributes and precalibrated lens distorsion parameters
        for rigid cameras in a stereo vision arrangement based on configuration file specifications.
       
        *args:
            project: your Metashape project\n
            config_data: content of the project configuration file\n
            save_project: (True/False, active_chunk.label)
        
        Returns:
            Updated Metashape project
        '''
        
        # process logging and console output
        print('Metashape workflow: (OPT) setting sensor parameters')
        project.logging('Calibration: sensor calibration set from config file')
    
        # rename sensors of a rigid camera installation according to camera names
        # and then link sensor to the camera
        if project.stereo_RGB == True or project.stereo_IR == True:
            
            # add new sensor in multiframe projects, each image line == one sensor
            while len(project.chunk.sensors) != len(project.chunk.cameras):
                project.chunk.addSensor()
                
            for i, sensor in enumerate(project.chunk.sensors):
                sensor.label = project.chunk.cameras[i].label
                project.chunk.cameras[i].sensor = sensor

        for i, camera in enumerate(project.chunk.cameras):

            sensor_att          = config_data['metashape']['setup'][f'sensor{i+1}']

            sensor              = camera.sensor
            sensor.label        = camera.label
            
            sensor.focal_length = sensor_att['general']['constant']
            sensor.pixel_height = sensor_att['general']['pix_size']
            sensor.pixel_width  = sensor_att['general']['pix_size']
            sensor.width        = sensor_att['general']['width']
            sensor.height       = sensor_att['general']['height']
            
            if sensor_att['general']['type'].lower() == 'frame':
                sensor.type     = Metashape.Sensor.Type.Frame
            if sensor_att['general']['type'].lower() == 'cylindrical':
                sensor.type     = Metashape.Sensor.Type.Cylindrical              
            if sensor_att['general']['type'].lower() == 'spherical':
                sensor.type     = Metashape.Sensor.Type.Spherical
            if sensor_att['general']['type'].lower() == 'fisheye':
                sensor.type     = Metashape.Sensor.Type.Fisheye         
                
            sensor.black_level  = sensor_att['spectral']['black_level']
            sensor.sensitivity  = sensor_att['spectral']['sensitivity']
            sensor.bands        = sensor_att['spectral']['bands']
            
            focal_len           = sensor_att['general']['constant']
            pixel_size          = sensor_att['general']['pix_size']
            
            cal                 = Metashape.Calibration()
            cal.width           = sensor_att['general']['width']
            cal.height          = sensor_att['general']['height']
            
            for item in sensor_att['initial']:
                if item == 'fixed_cal' or item == 'fixed_param':
                    continue
                if item == 'f':
                    if sensor_att['initial'][item][0] == True:
                        cal.f = sensor_att['initial'][item][1]
                    if sensor_att['initial'][item][1] == False:
                        cal.f = focal_len/pixel_size
                else:
                    setattr(cal, item, sensor_att['initial'][item]/pixel_size)

            sensor.user_calib        = cal
            
            sort_order               = ['F', 'Cx', 'Cy', 'B1', 'B2', 'K1', 'K2', 'K3', 'K4', 'P1', 'P2']
            sort_list                = [i.capitalize() for i in sensor_att['initial']['fixed_param']]
            sorted_list              = sorted(sort_list, key=lambda x: sort_order.index(x))
            
            sensor.fixed_calibration = sensor_att['initial']['fixed_cal']
            sensor.fixed_params      = sorted_list

        # save project and redefine the working chunk            
        if save_project[0] == True:
           project.saveMetashapeProject(active_chunk=save_project[1])

        return project