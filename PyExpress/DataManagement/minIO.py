import os
from   minio import Minio
import PyExpress.DataManagement as adm
import PyExpress.UtilityTools   as hlp

class MinIO():
    
    def __init__(self, config_MinIO: str, temp_dir: str='./', get_filelist=True):
        
        '''
        Is called when an instance of the MinIO class is being created. 
        
        *args:
            config_MinIO: full path to the project configuration file\n
            temp_dir: path to a temporary folder for downloaded images\n
            get_filelist: automatically create a file list based on config file specifications
        '''

        config = hlp.open_parameters(config_MinIO)
            
        self.conn_info   = config['connectionInfo']['info']
        self.server      = config['connectionInfo']['server']
        self.port_API    = config['connectionInfo']['portAPI']
        self.region_API  = config['connectionInfo']['regionAPI'] 
        self.url         = config['connectionInfo']['url']
        self.bucket      = config['bucketInfo']['name']
        self.prefix      = config['bucketInfo']['campaign']
        self.recursive   = config['filters']['recursive']
        self.str_filter  = config['filters']['string']
        self.list_filter = config['filters']['list']

        self.acc_key     = config['credentials']['accessKey']
        self.sec_key     = config['credentials']['secretKey']
        
        self.temp_dir   = temp_dir
            
        self.client   = self._define_client()
        self.filelist = list()
        
        if get_filelist == True:
            self.filelist  = self.get_objectlist(client        = self.client,
                                                 bucket        = self.bucket,
                                                 prefix        = self.prefix,
                                                 recursive     = self.recursive,
                                                 string_filter = self.str_filter, 
                                                 list_filter   = self.list_filter)    

    def _define_client(self):
        
        ''' Creates and returns an instance of a MinIO client for use. '''
        
        if self.conn_info.lower() == 'url':
            endpoint = self.url
        else:
            endpoint = ':'.join([self.server, self.port_API])
            
        client = Minio(endpoint=endpoint, access_key=self.acc_key, 
                       secret_key=self.sec_key, secure=True)
        
        return client


    def get_objectlist(self, client: object, bucket: str, prefix=None, recursive=True,
                        string_filter=[False,''], list_filter=[False, 'AND', list()]):
        
        ''' 
        Lists objects/files in a specified MinIO bucket. 
        The object list can be filtered by (a) a specified filename prefix, 
        (b) a specified string within the filename, and/or (c) using a list of specified strings.
            
        *args:
            client: instance of a MinIO client to interact with the service\n
            bucket: name of the MinIO bucket (container for objects)\n
            prefix: the beginning of the file path to filter\n
            recursive: whether to list files in subdirectories (True/False)\n
            string_filter: [True/False, specified substring used to filter a given file list]\n
            list_filter: [True/False, AND/OR, list of substrings]
        
        Returns:
            Filtered list of minIO file paths
        '''
        
        objects = client.list_objects(bucket_name=self.bucket, prefix=self.prefix, recursive=True)
        objects = [obj.object_name for obj in objects]
        
        if string_filter[0] == False and list_filter[0] == False:
            filtOBJ = objects
            
        if string_filter[0] == True and list_filter[0] == False:
            filtOBJ = self.filter_filelist_by_string(filelist=objects, string_filter=string_filter[1])
        
        if string_filter[0] == False and list_filter[0] == True:
            filtOBJ = self.filter_filelist_by_stringlist(filelist=objects, list_filter=list_filter[1:])
        
        if string_filter[0] == True and list_filter[0] == True:
            filtOBJ = self.filter_filelist_by_string(filelist=objects, string_filter=string_filter[1])
            filtOBJ = self.filter_filelist_by_stringlist(filelist=filtOBJ, list_filter=list_filter[1:])
            
        return filtOBJ
        
    def filter_filelist_by_string(self, filelist: list, string_filter: str):
        
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
    
    def filter_filelist_by_stringlist(self, filelist: list, list_filter: list):
        
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
        
        filtOBJ = []
        
        if list_filter[0] == 'AND':
            filtOBJ = filelist
            for item in list_filter[1]:
                filtOBJ = ([file for file in filtOBJ if item in file])

        if list_filter[0] == 'OR':
            filtOBJ = []
            for item in list_filter[1]:
                filtOBJ.extend([file for file in filelist if item in file])
                
        return filtOBJ


    def download_from_minio(self, as_path=False):

        ''' 
        Downloads all files listed in the MinIO client class parameter 
        ‘filelist’ to the path specified in the 'temp_dir' parameter.
        
        *args:
            as_path: [True, False]
                True - creates a path from the MinIO filepath with '_' as the separator\n
                False - creates the exact directory structure as in the MinIO bucket
            
        '''
        
        for file in self.filelist:
            
            file_norm   = os.path.normpath(file)
            
            if as_path == False:
                file_prefix = file_norm.split(os.sep)[-2]
                file_suffix = file_norm.split(os.sep)[-1]
                filename    = f'{file_prefix}_{file_suffix}'

            if as_path == True:
                filename = file
            
            destination = os.path.join(self.temp_dir, filename)
            
            adm.Local.create_directory(dir_path=os.path.dirname(destination))
            
            self.client.fget_object(bucket_name=self.bucket, 
                                    object_name=file, file_path=destination)

    def upload_to_minio(self, filelist: list, directory: str):
        
        '''
        Uploads data to a new object path, created dynamically.
        
        *args:
            filelist: list of file names\n
            directory: name of target directory, created dynamically
        '''
        
        directory = os.path.normpath(f'/{directory}')
        directory = directory.replace('\\', '/')
        
        for file in filelist:
            
            path = os.path.normpath(file)
            path = path.replace('\\', '/')
            
            obj  = f'{directory}/{os.path.basename(path)}'
            
            self.client.fput_object(bucket_name = self.bucket, 
                                    object_name = obj, 
                                    file_path   = path)