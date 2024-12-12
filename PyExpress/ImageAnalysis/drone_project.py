from ._project import _MetashapeProject

class DroneProject(_MetashapeProject):

    def __init__(self,
                 config_data: dict,
                 project_dir: str,
                 image_dir:   str,
                 config_name: str):

        
        self.sensor_type    = config_data['metashape']['general']['type'] 
        
        self.drone_IR       = False
        self.drone_RGB      = False
        self.stereo_IR      = False
        self.stereo_RGB     = False
        
        if self.sensor_type == 'IR':
            self.drone_IR   = True
            
        if self.sensor_type == 'RGB':
            self.drone_RGB  = True
        
        if self.sensor_type == 'Multi':
            pass

        super().__init__(config_data, project_dir, image_dir, config_name)

    
    def _setVegetationIndex(self, vegetation_index: list()):
        
        '''
        Adds a vegetation index to the multispectral Metashape project, defining how the raster band color information should be processed.

        *args:
            vegetation_index: Valid string for a raster band combination based on the spectral channels of the footage.
                              For example, NDVI for the P4 multispectral drone: ["(B5 - B3) / (B5 + B3)"]
        '''

        if self.drone_IR == True:
            self.vegetation_index = vegetation_index
        
        if self.drone_RGB == True:
            self.vegetation_index = vegetation_index


    def _setVegetationIndexRange(self, index_range: list(), auto_range=False):

        '''
        Sets raster transformation range for a designated raster, e.g. DEM or orthomosaic.
        
        *args:
            index_range: (lowest index value, highest index value)
            auto_range: set raster transformation range automatically from its histogram
        '''
        
        if auto_range == True:          
            self.chunk.raster_transform.calibrateRange()
        else:
            self.chunk.raster_transform.range = index_range
            
            
    def _setVegetationIndexPalette(self, index_palette: dict()):
        
        '''
        Sets raster transformation palette for a designated raster, e.g. DEM or orthomosaic.
        
        *args:
            index_palette: 
                dictionary for e.g. NDVI:\n
                    {-1.0: (5, 24, 82),\n
                     0.0: (255, 255, 255),\n
                     0.1: (191, 165, 127),\n
                     0.3: (135, 184, 0),\n
                     0.6: (0, 115, 0),\n 
                     1.0: (0, 0, 0)}
        '''
        
        self.chunk.raster_transform.palette = index_palette


    def applyVegetationIndex(self,
                             config_data:  dict,
                             save_project: tuple = (False, '')):
        
        '''
        Sets raster transformation specified in the configuration file to the photogrammetric project.
        This contains setting of raster transformation index, range, formula & palette.
        
        *args:
            config_data: content of the project configuration file
            save_project: (True/False, *active_chunk*.label)
        '''

        print('Metashape workflow: (OPT) applying vegetation index as raster transformation')
        
        col_palette = {a: tuple(b) for a,b in config_data['metashape']['vegetation']['palette'].items()}
        auto_range  = config_data['metashape']['vegetation']['rangeAuto']
        
        if self.drone_IR == True:
            item_list   = config_data['metashape']['vegetation']['indexIR']
            ind_range   = tuple(config_data['metashape']['vegetation']['rangeIR'])

        if self.drone_RGB == True:
            item_list = config_data['metashape']['vegetation']['indexMulti']
            ind_range = tuple(config_data['metashape']['vegetation']['rangeMulti'])      

        self._setVegetationIndex(vegetation_index=item_list)        
        self._setVegetationIndexRange(index_range=ind_range, auto_range=False)
        self._setVegetationIndexPalette(index_palette=col_palette)
        
        self.chunk.raster_transform.formula = self.vegetation_index
        self.chunk.raster_transform.enabled = True        
        
        if auto_range == True:
            self.chunk.raster_transform.calibrateRange()
        
        super().logging(f'Raster transformation index (vegetation monitoring): {self.vegetation_index}')
        super().logging(f'Raster transformation range (vegetation monitoring): {self.chunk.raster_transform.range}')
        
        # save project and redefine the working chunk
        if save_project[0] == True:            
            super().saveMetashapeProject(active_chunk=save_project[1])