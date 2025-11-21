# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum f√ºr Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

# https://www.quantum.com/de/produkte/object-storage/
#
# required for S3 usage:
# boto3==1.35.* python-dotenv==1.1.* requests==2.32.*
#
# pip install boto3==1.35.* python-dotenv==1.1.* requests==2.32.*

import os, sys
import yaml, json
import requests, boto3
from   botocore.exceptions import ClientError

class QuantumActiveScale():
    
    def __init__(self, config_QAS: object, temp_dir: str='./', get_filelist=True):

        '''
        Is called when an instance of the Quantum_ActiveScale S3 class is being created. 
        
        *args:
            config_QAS: full path to the project configuration file\n
            temp_dir: path to a temporary folder for downloaded images\n
            get_filelist: automatically create a file list based on config file specifications
        '''
        
        # get configuration parameters from file
        if isinstance(config_QAS, dict):
            config = config_QAS
        else:
            config = self._open_parameters(config_QAS)
        
        # connection info for the call of a S3 client
        self.bucket_name           = config['bucket_info']['name']
        self.aws_access_key_id     = config['credentials']['access_key']
        self.aws_secret_access_key = config['credentials']['secret_key']
        self.endpoint_url          = config['connection_info']['endpoint_url']
        self.prefix                = config['bucket_info']['prefix']
        
        # for item in config['connection_info']['kwargs']:
        #     self.item              = config['connection_info']['kwargs'][item]
        #     ...
            
        # filter your object list for objects of interest
        self.recursive             = config['filters']['recursive']
        self.str_filter            = config['filters']['string']
        self.list_filter           = config['filters']['list']
        
        # create the client and optionally attach a filelist
        self.client                = self._define_client()
        self.filelist              = list()
        self.temp_dir              = temp_dir
        
        if get_filelist == True:
            self.filelist = self.get_objectlist(client        = self.client,
                                                bucket        = self.bucket_name,
                                                prefix        = self.prefix,
                                                recursive     = self.recursive,
                                                string_filter = self.str_filter, 
                                                list_filter   = self.list_filter) 

    def _modul_version_controll(self, modul: str):
        
        ''' Controlls versions of an installed python module.
        
        *args:
            modul: modul name string

        Retruns:
            Module version as string
        '''
        
        import pkg_resources

        for dist in pkg_resources.working_set:
            if modul in dist.project_name.lower():
                return dist.version
                
    def _open_parameters(self, path: str):
            
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

    def _create_directory(self, dir_path: str):
        
        '''
        Creates a new directory in the target path.
        
        *args:
            dir_path: full path of the directory to be created
        '''
    
        os.makedirs(dir_path, exist_ok=True)
        
    def _define_client(self):
        
        ''' Creates and returns an instance of a MinIO client for use. '''
        
        if not self.endpoint_url.startswith(('http://', 'https://')):
            self.endpoint_url = 'https://' + self.endpoint_url

        client = boto3.client('s3',
                              endpoint_url          = self.endpoint_url,
                              aws_access_key_id     = self.aws_access_key_id,
                              aws_secret_access_key = self.aws_secret_access_key)
        return client


    def get_objectlist(self, client: object, bucket: str, prefix=None, recursive=True,
                       string_filter=[False,''], list_filter=[False, 'AND', list()]):
        
        ''' 
        Lists objects/files in a specified QAS S3 bucket. 
        The object list can be filtered by (a) a specified filename prefix, 
        (b) a specified string within the filename, and/or (c) using a list of specified strings.
            
        *args:
            client: instance of a QAS S3 client to interact with the service\n
            bucket: name of the QAS S3 bucket (container for objects)\n
            prefix: the beginning of the file path to filter\n
            recursive: whether to list files in subdirectories (True/False)\n
            string_filter: [True/False, specified substring used to filter a given file list]\n
            list_filter: [True/False, AND/OR, list of substrings]
        
        Returns:
            Filtered list of minIO file paths
        '''
        
        ### the list_objects_v2 method is explicitly listing only 1000 objects by default
        # objects   = self.client.list_objects_v2(Bucket = bucket, Prefix = prefix)['Contents']
        # objects   = [obj['Key'] for obj in objects]
        
        ### the paginator method creates an iterator listing 1000 objects per page
        paginator     = self.client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
        objects       = []
        
        for page in page_iterator:
            if 'Contents' in page:
                objects.extend([obj['Key'] for obj in page['Contents']])        
        
        if self.str_filter[0] == False and self.list_filter[0] == False:
            filtOBJ = objects
            
        if self.str_filter[0] == True and self.list_filter[0] == False:
            filtOBJ = self.filter_filelist_by_string(filelist=objects, string_filter=self.str_filter[1])
        
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

    def download_file(self, as_path=False):

        ''' 
        Downloads all files listed in the QAS S3 client class parameter 
        to the path specified in the 'temp_dir' parameter.
        
        *args:
            as_path: [True, False]
                True - creates a path from the QAS filepath with '_' as the separator\n
                False - creates the exact directory structure as in the QAS bucket
            
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
            
            self._create_directory(dir_path=os.path.dirname(destination))
            
            # ### method 1: working with boto3 version higher than 1.35 
            # url = self.client.generate_presigned_url('get_object',
            #                                          Params={'Bucket': self.bucket_name, 
            #                                                  'Key': file},
            #                                          ExpiresIn=3600)
            
            # response = requests.get(url, stream=True)
            
            # with open(destination, 'wb') as f_write:
            #     for chunk in response.iter_content(chunk_size=8192):
            #         f_write.write(chunk)
            
            # ### method 2: working only with boto3 version 1.35 or less
            self.client.download_file(Bucket   = self.bucket_name, 
                                      Key      = file,
                                      Filename = destination)

    def download_fileobject(self, as_path=False):

        ''' 
        Downloads all objects listed in the QAS S3 client class parameter 
        to the path specified in the 'temp_dir' parameter.
        
        *args:
            as_path: [True, False]
                True - creates a path from the QAS filepath with '_' as the separator\n
                False - creates the exact directory structure as in the QAS bucket
            
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
            
            self._create_directory(dir_path=os.path.dirname(destination))
            
            # ### method 1: working with boto3 version higher than 1.35 
            # url = self.client.generate_presigned_url('get_object',
            #                                          Params={'Bucket': self.bucket_name, 
            #                                                  'Key': file},
            #                                          ExpiresIn=3600)
            
            # response = requests.get(url, stream=True)
            
            # with open(destination, 'wb') as f_write:
            #     for chunk in response.iter_content(chunk_size=8192):
            #         f_write.write(chunk)
            
            # ### method 2: working only with boto3 version 1.35 or less
            with open(destination, 'wb') as f_object:
                self.client.download_fileobj(Bucket  = self.bucket_name, 
                                             Key     = file, 
                                             Fileobj = f_object)
        
    def upload_to_qas_s3(self, filelist: list, directory: str):
        
        '''
        Uploads data to a new object path, created dynamically.
        
        *args:
            filelist: list of file names\n
            directory: name of target directory, created dynamically
        '''
        
        directory = os.path.normpath(f'{directory}')
        directory = directory.replace('\\', '/')
        
        for file in filelist:
            
            path = os.path.normpath(file)
            path = path.replace('\\', '/')
            
            obj  = f'{directory}/{os.path.basename(path)}'
            
            self.client.upload_file(Filename = file,
                                    Bucket   = self.bucket_name,
                                    Key      = obj)
        
    def delete_file_from_QAS_s3(self, file='', filelist=list()):
        
        '''
        Delets a file or a list of files from a given bucket.
        
        *args:
            file: must exactly match a key on the bucket\n
            filelist: list of valid keys to be deleted
        '''
        
        if not isinstance(filelist, list):
            print('given filelist is not a list. controll type.'); sys.exit()
        
        if not filelist:
            self.client.delete_object(Bucket = self.bucket_name,
                                      Key    = file)
        if filelist:
            self.client.delete_objects(Bucket = self.bucket_name,
                                       Delete={'Objects': [{'Key': k} for k in filelist], 'Quiet': True})