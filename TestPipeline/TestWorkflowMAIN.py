"""
Main control script for automatically managing an entire workflow to generate 
3D spatial data from raw image files acquired by UAV campaigns.

@author: Martin Kobe, martin.kobe@ufz.de; Rikard Graß, rikard.grass@ufz.de

@status: 11/2024; part of the EXPRESS Project at UFZ Leipzig.

*******************************************************************************
NOTE: Carefully follow all necessary steps outlined in the Tutorial
      './'PyExpressTutorial.pdf' before running the following main routine.
"""

# Import necessary tools: built-in, installed
import os, time, sys

# If PyExpress is not found, update the system path using the command:
# sys.path.append(f'{os.getcwd()}\\pyexpress')

# Import PyExpress and its subclasses/methods
import PyExpress
import PyExpress.UtilityTools as hlp

# Time tracking
start_time = time.time()

###############################################################################
# USER INPUT: definitions, path of config file for parameterinput, project path
#
# Example for a new project:
configPath_NEW = os.getcwd()
configFile_NEW = 'TEST_config_NEW.yaml'
# Example for an existing project:
configPath_EXI = os.getcwd()
configFile_EXI = 'TEST_config_EXI.yaml'
# Choose which project to use by changing the object name suffix:
config_dir     = configPath_NEW
config_file    = configFile_NEW

###############################################################################
# AUTOMATIC SETTINGS BASED ON USER INPUT AND CONFIGURATION FILE CONTENT
#
# Load the configuration file's content
config_dir   = os.path.normpath(config_dir)
config_path  = os.path.join(config_dir, config_file)
config_data  = hlp.open_parameters(config_path)

# Extract processing steps to be performed beforehand
new_project  = config_data['input']['general']['new_project']
transfer_img = config_data['input']['image']['preproc']['transfer']
preproc_img  = config_data['input']['image']['preproc']['convert']
del_temp_dir = config_data['input']['image']['preproc']['delete_tmp']

# Retrieve specifications for the Metashape project
transfer_dir = config_data['input']['image']['source']['temp']
data_type    = config_data['metashape']['general']['type']

###############################################################################
# NEW PROJECT: Example workflow for photogrammetric data analysis

if new_project == True:
    
# a) Create a basic project directory structure
    img_dir, prj_dir = hlp.create_UAV_project(config_data = config_data, 
                                              config_path = config_path)
       
# b) Transfer images from various sources (local, minIO) to either
#    - project image folder (no preprocessing) or
#    - temp image folder (preprocessing required)
#    NOTE: In this test example, the project image folder is defined as default
    if transfer_img == True:
        if data_type == 'IR':  transfer_dir = img_dir                     # (!)
        if data_type == 'RGB': transfer_dir = img_dir                     # (!)
        
        hlp.transfer_images(config_data = config_data, 
                            dest_dir    = transfer_dir, 
                            recursive   = True)

# c) Preprocess raw image data based on user and project requirements
#    NOTE: In this test example, already preprocessed images are used/provided 
    pass
    
# d) Run example workflow for a UAV-based vegetation monitoring project
    MultiProject = PyExpress.WorkflowExamples.TEST_workflow(config_data = config_data,
                                                            prj_dir     = prj_dir,
                                                            img_dir     = img_dir,
                                                            config_name = config_file)     

# e) Optionally delete log file after processing
    if input('Delete lock file [y,n]?: ') == 'y': MultiProject.doc.clear()

###############################################################################
# EXISTING PROJECT: Resume or recalculate photogrammetric data analysis

if new_project == False:

# a) Open a basic existing project directory structure
    img_dir, prj_dir = hlp.open_project(config_data = config_data, 
                                        config_path = config_path)
    
# b) Run example workflow for a UAV-based vegetation monitoring project     
    MultiProject = PyExpress.WorkflowExamples.TEST_workflow(config_data = config_data,
                                                            prj_dir     = prj_dir,
                                                            img_dir     = img_dir,
                                                            config_name = config_file)          

# c) Optionally delete log file after processing
    if input('Delete lock file [y,n]?: ') == 'y': MultiProject.doc.clear()
    
###############################################################################
# Execution time log
hlp.log(start_time=start_time, string='\nAutomated pipeline execution time', dim='HMS')