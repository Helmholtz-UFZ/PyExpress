from ._project import _MetashapeProject

class StereoProject(_MetashapeProject):

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
        
        if self.sensor_type == 'RGB':
            self.stereo_RGB = True
        
        if self.sensor_type == 'IR':
            self.stereo_IR = True
        
        if self.sensor_type == 'Multi':
            pass

        super().__init__(config_data, project_dir, image_dir, config_name)
    

    def camera_count(self):      
        pass