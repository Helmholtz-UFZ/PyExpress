# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

import glob, os, shutil

class Local():
        
    def get_filelist(file_dir: str, ext: str, recursive=False):
        
        '''
        Returns a list of files of a specified format.
        
        *args:
            file_dir: local image storage directory\n
            ext: file format\n
            recursive: also list files in subdirectories
        
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
    
    def move_directory(source_path: str, target_path: str):
        
        '''
        Moves a directory and its content from a source location to target destination.
        
        *args:
            source_path: full path to the directory to be moved\n
            target_path: full path to the destination directory
        '''
        
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            
        shutil.move(source_path, target_path)
        
    @staticmethod
    def move_file(source_path: str, target_path: str):
        
        '''
        Moves a file from a source location to target directory.
        
        *args:
            source_path: full path to the file to be moved\n
            target_path: full path to the destination directory
        '''
        
        file_dest_path = os.path.join(target_path, os.path.basename(source_path))
        
        if os.path.exists(file_dest_path):
            os.remove(file_dest_path)
            
        shutil.move(source_path, target_path)
    
    def move_filelist(file_list: list, target_path: str):
        
        '''
        Moves all files specified in a list to target directory.
        
        *args:
            file_list: a list of full file paths to be moved\n
            target_path: full path to the destination directory
        '''
        
        for file in file_list:
            Local.move_file(source_path=file, target_path=target_path)
    
    def copy_directory(source_path: str, target_path: str):
        
        '''
        Recursively copies a directory and its content from a source location to target directory.
        
        *args:
            source_path: full path to the directory to be copied\n
            target_path: full path to the destination directory
        '''
    
        shutil.copytree(source_path, target_path)
     
    @staticmethod
    def copy_file(source_path: str, target_path: str):
        
        '''
        Copies a file from a source location to target directory.
        
        *args:
            source_path: full path of the file to be copied\n
            target_path: destination directory, where the file will be saved
        '''        
        
        shutil.copy(source_path, target_path)
    
    def copy_filelist(file_list: list, target_path: str):
        
        '''
        Copies all files specified in a list to target directory.
        
        *args:
            file_list: a list of full file paths to be copied\n
            target_path: destination path where the files will be saved
        '''
        
        for file in file_list:
            Local.copy_file(source_path=file, target_path=target_path)
    
    @staticmethod
    def remove_file(file_path: str):
        
        '''
        Removes/deletes a file from target directory.
        
        *args:
            file_path: full path to the file to be removed\n
        '''
        
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def remove_filelist(file_list: list):
    
        '''
        Removes/deletes all files specified in a list from target directory.
        
        *args:
            file_list: a list of full file paths to be removed
        '''
        
        for file in file_list:
            Local.remove_file(file)
    
    def remove_directory(dir_path: str):
        
        '''
        Removes/deletes a directory and all of its contents.
        
        *args:
            dir_path: full path of the directory to be removed
        '''
        
        shutil.rmtree(dir_path, ignore_errors=True)
    
    def create_directory(dir_path: str):
        
        '''
        Creates a new directory in the target path.
        
        *args:
            dir_path: full path of the directory to be created
        '''
    
        os.makedirs(dir_path, exist_ok=True)