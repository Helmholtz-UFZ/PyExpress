import json, yaml, os, re, glob, sys, time

from   io                       import StringIO
import PyExpress.DataManagement as     adm

###############################################################################
# parameter file handling: format conversion, open, save, ...    
def convert_JSON_to_YAML(source_path: str, save_path: str, directory=False, recursive=False):

    '''
    Converts the contents of a JSON file into YAML format and saves it.
    
    *args:
        if directory == True:
            source_path: directory with JSON files\n
            save_path:   directory, where converted YAML files will be saved\n
            recursive:   if True, subdirectories will also be searched for JSON files
        if directory == False:
            source_path: full file path of a specific JSON file\n
            save_path:   directory, where converted YAML file will be saved\n
            recursive:   not needed; keep as False
    '''
    
    if not directory:
        data  = open_parameters(source_path)
        name_ = os.path.basename(source_path).replace('json', 'yaml')
        dest_ = os.path.join(save_path, name_)
        adm.Local.create_directory(dir_path=os.path.dirname(dest_))

        with open(dest_, 'w') as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
    
    if directory:
        fileList = get_filelist(file_dir=source_path, ext='.json', recursive=recursive)
        
        for file in fileList:
            data  = open_parameters(file)
            dest_ = file.replace(source_path, save_path).replace('.json', '.yaml')            
            adm.Local.create_directory(dir_path=os.path.dirname(dest_))            
            
            with open(dest_, 'w') as ff:
                yaml.dump(data, ff, default_flow_style=False, sort_keys=False)

def convert_YAML_to_JSON(source_path: str, save_path: str, directory=False, recursive=False):
    
    '''
    Converts the contents of a YAML file into JSON format and saves it.
    
    *args:        
        if directory == True:
            source_path: directory with YAML files\n
            save_path:   directory, where converted JSON files will be saved\n
            recursive:   if True, subdirectories will also be searched for YAML files
        if directory == False:
            source_path: full file path of a specific YAML-file\n
            save_path:   directory, where converted JSON file will be saved\n
            recursive:   not needed; keep as False
    '''
    
    if not directory:            
        data  = open_parameters(source_path)
        name_ = os.path.basename(source_path).replace('.yaml', '.json')
        dest_ = os.path.join(save_path, name_)
        adm.Local.create_directory(os.path.dirname(dest_))
        
        with open(dest_, 'w') as file:            
            json.dump(data, file, indent=2)

    if directory:        
        fileList  = get_filelist(file_dir=source_path, ext='.yaml', recursive=recursive)
        
        for file in fileList:
            data  = open_parameters(file)
            dest_ = file.replace(source_path, save_path).replace('.yaml', '.json')
            adm.Local.create_directory(os.path.dirname(dest_))
            
            with open(dest_, 'w') as ff:
                json.dump(data, ff, indent=2)

def open_parameters(path: str):
    
    ''' 
    Returns dictionary of parameters from a configuration file. Supported file formats are json, yaml.
    
    *args:
        path: absoulte path to the configuration file
    
    Returns:
        Dictionary with file content
    '''
    
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r') as file:
            return yaml.safe_load(file)
            
    elif path.endswith('.json'):
        with open(path, 'r') as file:
            return json.load(file)
    else:
        raise ValueError("Unsupported file format."
                         "Please provide a YAML (.yaml, .yml) or JSON (.json) file.")
    
###############################################################################
# file handling: download, storage, copy, etc

def get_filelist(file_dir: str, ext: str, recursive=False):
    
    '''
    Returns a list of files of a specified format.
    
    *args:
        file_dir: local image storage directory\n
        ext: file format\n
        recursive: list files from subdirectories as well
    
    Returns:
        List of files
    '''
    
    if recursive == True:
        filepath = os.path.normpath(os.path.join(file_dir, '**', '*'))
        filelist = glob.glob(filepath, recursive=True)
        
        return [f for f in filelist if f.lower().endswith(ext.lower())]
    
    if recursive == False:
        filepath = os.path.normpath(os.path.join(file_dir, '*'))
        filelist = glob.glob(filepath, recursive=False)
        
        return [f for f in filelist if f.lower().endswith(ext.lower())]

def filter_filelist_by_string(filelist: list, string_filter: str):
    
    ''' 
    Filters a given list of file paths by a specified substring. 
    
    *args:
        filelist: list of complete file paths \n
        string_filter: specified substring used to filter a given filelist
    
    Returns:
        Filtered list of file paths
    '''
    
    filtOBJ = [file for file in filelist if string_filter in file]
    
    return filtOBJ

def filter_filelist_by_stringlist(filelist: list, list_filter: list):
    
    ''' 
    Filters a given list of file paths by multiple specified substrings. 
    
    *args:
        filelist: list of complete file paths\n
        list_filter: ['AND/OR', [list of substrings]]\n
            AND --> keeps files containing all specified substrings\n
            OR  --> keeps files containing at least one specified substring
    
    Returns:
        Filtered list of file paths
    '''
    
    if list_filter[0] == 'AND':
        filtOBJ = filelist
        for item in list_filter[1]:
            filtOBJ = ([file for file in filtOBJ if item in file])

    if list_filter[0] == 'OR':
        filtOBJ = []
        for item in filelist[1]:
            filtOBJ.extend([file for file in filelist if item in file])
            
    return filtOBJ
    
def extract_date_stamps(file_list: list, pattern: str = ''):
    
    ''' 
    Extracts the date pattern from filenames in a given list by matching them against a specified regex pattern.
    
    *args:
        file_list: a list of file names\n
        pattern: regex pattern, for more information see https://docs.python.org/3/library/re.html
    
    Returns:
        List of date strings
    '''
        
    date_stamps = []
    pattern = re.compile(pattern)
    
    for path in file_list:
        match = pattern.search(path)
        if match:
            date_stamps.append(match.group(1))
            
    return date_stamps

def transfer_images(config_data: dict, dest_dir: str, recursive=True):
    
    ''' 
    Transfers images from a given source (local, minio) to target directory.
    
    Args:
        config_data: full path to your project configuration file\n
        dest_dir: target directory for images to copy\n
        recursive: collect and copy image files also from subdirectories
    '''
        
    source    = config_data['input']['image']['source']['type']
    uri_minio = config_data['input']['image']['source']['minio']
    uri_local = config_data['input']['image']['source']['local']
    extension = config_data['input']['image']['format']['raw']

    proj_type = config_data['input']['project']['type']
    
    adm.Local.remove_directory(dir_path=dest_dir)
    
    if not source in ['aws', 'nextcloud', 'local', 'minio']:
        raise NameError(f'"{source}" is an unknown image location.')

    # console logging
    print(f'Metashape preparation:  copying images from {source} source')
    
    if source == 'minio':
        cloudData = adm.MinIO(config_MinIO=uri_minio, temp_dir=dest_dir, get_filelist=False)        
        cloudData.filelist = cloudData.get_objectlist(client        = cloudData.client,
                                                      bucket        = cloudData.bucket,
                                                      prefix        = cloudData.prefix,
                                                      recursive     = cloudData.recursive,
                                                      string_filter = cloudData.str_filter, 
                                                      list_filter   = cloudData.list_filter)
        
        cloudData.download_from_minio()

    if source == "local":
        files      = get_filelist(file_dir=uri_local, ext=extension, recursive=recursive)        
        files      = [os.path.normpath(file) for file in files]
        start_time = time.time()
        
        for file in files:
            
            if proj_type == 'UAV':
                file_prefix     = file.split(os.sep)[-2]
                file_suffix     = file.split(os.sep)[-1]
                file_name       = f'{file_prefix}_{file_suffix}'
                destination     = os.path.join(dest_dir, file_name)            
                        
            if proj_type == 'stereo':                
                file_name       = file.split(os.sep)[-1]
                sensor_dir      = file.split(os.sep)[-2]
                destination     = os.path.join(dest_dir, sensor_dir, file_name)
                
            adm.Local.create_directory(dir_path=os.path.dirname(destination))
            adm.Local.copy_file(source_path=file, target_path=destination)            

        log(start_time=start_time, string=f"{' ' * 24}execution time", dim='HMS') 


###############################################################################
# project structure setup

def create_UAV_project(config_data: dict, config_path: str, copy_markers=True):

    ''' 
    Creates an empty UAV project structure. 
    The project name and the target project path are specified 
    in the configuration file’s input section (general, campaign, and project). 
    Copies the configuration file to the target project path. 
    
    *args:
        config_data: content of the project configuration file\n
        config_path: full path to your project configuration file\n
        copy_markers: copy marker files to new project directory
    '''
        
    # console logging
    print('Metashape preparation:  creating metashape project structure (UAV)')
    
    # get data from parameter object
    if config_data['input']['general']['ID_source'] == 'campaign':
        date         = config_data['input']['campaign']['date']
        flightTime   = config_data['input']['campaign']['time']
        location     = config_data['input']['campaign']['location']
        drone        = config_data['input']['campaign']['drone']
        channel      = config_data['input']['campaign']['sensor']
        add_info     = config_data['input']['campaign']['ID_info']
        project_name = f'{date}_{flightTime}_{location}_{drone}_{channel}'
        project_name = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', project_name))
        
    if config_data['input']['general']['ID_source'] == 'string':
        project_name     = config_data['input']['general']['ID_string']        
        add_info         = ''

    project_path     = config_data['input']['project']['path']    
    project_path     = os.path.join(project_path, project_name)
    project_path     = os.path.normpath(project_path)

    image_data_path  = os.path.join(project_path, 'image_data')
    prj_dir          = os.path.join(project_path, 'metashape_prj')
    
    adm.Local.create_directory(dir_path=image_data_path)
    adm.Local.create_directory(dir_path=prj_dir)

    # copy parameterfile yaml or json to project directory
    conf_path = os.path.join(prj_dir, f'{project_name}_{add_info}_#1')
    conf_path = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', conf_path))
    conf_path = f'{conf_path}.{config_path.split(".")[-1]}'
    
    adm.Local.copy_file(source_path=config_path, target_path=conf_path)

    # copy marker files to project directory
    if copy_markers == True:
        copy_marker_ref(config_data=config_data, prj_dir=prj_dir)
    
    return image_data_path, prj_dir


def create_stereo_project(config_data: dict, config_path: str):
    
    '''
    Creates an empty stereo project structure.
    The project name and the target project path are specified in the configuration 
    file’s input section (general, campaign, and project). 
    Copies the configuration file to the target project path.
    
    *args:
        config_data: content of the project configuration file\n
        config_path: full path to the project configuration file  
    '''
    
    # console logging
    print('Metashape preparation:  creating metashape project structure (stereo)')
    
    # get project data from parameter object
    if config_data['input']['general']['ID_source'] == 'campaign':
        period           = config_data['input']['campaign']['date']
        location         = config_data['input']['campaign']['location']
        setup            = config_data['input']['campaign']['cameraID']
        add_info         = config_data['input']['campaign']['ID_info']
        channel          = config_data['input']['campaign']['sensor']
        project_name     = f'{period}_{location}_{setup}_{channel}'
        project_name     = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', project_name))
    
    if config_data['input']['general']['ID_source'] == 'string':
        project_name     = config_data['input']['general']['ID_string']
        add_info         = ''
        
    project_path     = config_data['input']['project']['path']    
    project_path     = os.path.join(project_path, project_name)
    project_path     = os.path.normpath(project_path)
    
    image_data_path  = os.path.join(project_path, 'image_data')
    prj_path         = os.path.join(project_path, 'metashape_prj')
    
    # create image and project data structure
    adm.Local.create_directory(dir_path=image_data_path)
    adm.Local.create_directory(dir_path=prj_path)
    
    # copy parameterfile YAML or JSON to project directory
    conf_path = os.path.join(prj_path, f'{project_name}_{add_info}_#1')
    conf_path = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', conf_path))
    conf_path = f'{conf_path}.{config_path.split(".")[-1]}'

    adm.Local.copy_file(source_path=config_path, target_path=conf_path)

    return image_data_path, prj_path


def open_project(config_data: str, config_path: str):
    
    '''
    Returns project and image paths of an N metashape project structure.
    
    *args:
        config_data: content of the project configuration file\n
        config_path: full path to the configuration file in target metashape project folder
    '''
    
    # console logging
    print('Metashape preparation:  catching metashape project directories')

    # get data from parameter object
    if config_data['input']['general']['ID_source'] == 'campaign':
        date         = config_data['input']['campaign']['date']
        flightTime   = config_data['input']['campaign']['time']
        location     = config_data['input']['campaign']['location']
        drone        = config_data['input']['campaign']['drone']
        channel      = config_data['input']['campaign']['sensor']
        add_info     = config_data['input']['campaign']['ID_info']
        project_name = f'{date}_{flightTime}_{location}_{drone}_{channel}'
        project_name = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', project_name))
        
    if config_data['input']['general']['ID_source'] == 'string':
        project_name     = config_data['input']['general']['ID_string']
        add_info         = ''    

    if config_data['input']['general']['ID_source'] == 'existing':
        project_name     = config_data['input']['general']['ID_string']        
        add_info         = ''
        
    project_path     = config_data['input']['project']['path']    
    project_path     = os.path.join(project_path, project_name)
    project_path     = os.path.normpath(project_path)

    image_data_path  = os.path.join(project_path, 'image_data')
    prj_dir          = os.path.join(project_path, 'metashape_prj')

    # copy parameterfile YAML or JSON to project directory
    conf_path = os.path.join(prj_dir, f'{project_name}_{add_info}_#1')
    conf_path = re.sub(r'^_+|_+$', '', re.sub(r'_{2,}', '_', conf_path))
    conf_path = f'{conf_path}.{config_path.split(".")[-1]}'
    
    while os.path.exists(conf_path):
        ind       = int(conf_path.split(".")[0].split('#')[-1])
        conf_path = f'{conf_path.split("#")[0]}#{ind+1}.{config_path.split(".")[-1]}'

    if os.path.abspath(conf_path) != os.path.abspath(config_path):
        adm.Local.copy_file(source_path=config_path, target_path=conf_path)
    
    # # define project and image path
    # prj_path        = os.path.dirname(config_path)
    # image_data_path = prj_path.replace('metashape_prj', 'image_data')
    
    return image_data_path, prj_dir


def copy_marker_ref(config_data: dict, prj_dir: str):
    
    '''
    Copies csv files with marker coordinates, marker image projections, 
    or reflectance panel information from the specified source 
    (as defined in the config file) to target project directory. 

    *args:
        config_data: content of the project configuration file\n
        prj_dir: target project directory
    '''
    
    refPan  = config_data['input']['reflectance']['use']
    GCP_GCS = config_data['input']['marker_reference']['use_GCP_meas']
    GCP_PCS = config_data['input']['marker_reference']['use_GCP_proj']
    
    # console logging
    print('Metashape preparation:  copying marker files to project directory')
    
    if refPan==True:
        reflectance_panel_path = config_data['input']['reflectance']['reflectancepanel_path']
        
    if GCP_GCS==True:
        gcp_path               = config_data['input']['marker_reference']['reference_path']
    
    if GCP_PCS==True:
        marker_projection_path = config_data['input']['marker_reference']['projections_path']
    
    if refPan==True and os.path.exists(reflectance_panel_path):
        reflectance_panel_prj_path = os.path.join(prj_dir, 'reflectance_panel.csv')
        adm.Local.copy_file(source_path=reflectance_panel_path, target_path=reflectance_panel_prj_path)
    if refPan==True and not os.path.exists(reflectance_panel_path):
        print(f"{' ' * 24}copy error: reflectance_panel.csv")
    
    if GCP_GCS==True and os.path.exists(gcp_path):        
        gcp_prj_path = os.path.join(prj_dir, 'marker_reference.csv')
        adm.Local.copy_file(source_path=gcp_path, target_path=gcp_prj_path)
    if GCP_GCS==True and not os.path.exists(gcp_path):  
        print(f"{' ' * 24}copy error: marker_reference.csv")
    
    if GCP_PCS==True and os.path.exists(marker_projection_path):        
        marker_projections_prj_path = os.path.join(prj_dir, 'marker_projections.csv')
        adm.Local.copy_file(source_path=marker_projection_path, target_path=marker_projections_prj_path)
    if GCP_PCS==True and not os.path.exists(marker_projection_path):
        print(f"{' ' * 24}copy error: marker_projections.csv")


###############################################################################
# others

def log(start_time, string='', dim='sek'):
    
    '''
    Displays the time difference from a specified start time and the current 
    time in the console.
    
    *args:
        start_time: time.time() object of the built-in Python module time\n
        string: message displayed together with time difference\n
        dim: choose an output format as follows\n
              ms  - milli seconds\n
              mus - micro seconds\n
              MS  - min:sec (default)\n
              HMS - hr:min:sec
    '''

    T_now       = time.time()
    T_elapsed   = T_now-start_time
    
    if dim=='HMS':
        TT = time.strftime('%H:%M:%S', time.gmtime(T_elapsed))
        print(f'{string} - {TT} hrs')
        
    if dim=='MS':
        TT = time.strftime('%M:%S', time.gmtime(T_elapsed))
        print(f'{string} - {TT} min')
    
    if dim=='ms':
        t_ms        = round(T_elapsed*1000, 2)
        print(f'{string} - {t_ms} ms')
    
    if dim=='mus':
        t_mus        = round(T_elapsed*1000 * 1000, 2)
        print(f'{string} - {t_mus} \u03BCs')


class suppress_stdout():
    
    '''
    Suppresses console output.
    Is not working for modules based on C or C++ (e.g. Metashape).
    
    Use:
        with suppress_stdout():
            print('Execute your syntax here; no console output will appear!')
    '''
    
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout