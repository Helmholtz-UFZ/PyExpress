# PyExpress

PyExpress is a Python package developed at UFZ Leipzig by the EXPRESS research project. Its main purpose is to:

1. provide a set of interfaces to regularly or irregularly acquire image and timeseries data from influxDB and SFTP servers,
2. perform a quality check for both image and timeseries data,
3. perform a photogrammic processing of the acquired image date and extract ortho images of both multispectral indices and RGB level,
4. archive the processed data and forward it to a grafana page.

To achieve that, the package includes a set of classes and functions, based on a workflow like structure. 
The goal is to deliver the functionality of loading the described data to a central processing unit, perform a quality control, photogrammicly process the image data and upload processed image and timeseries data to an end-user interface.

_An introduction on how to use the photogrammicProcessing sub-package is given in the exampleProcessing notebook._

## To-do’s:
#### _cleanup code_
- constanly check documentation!!!

#### _missing functionality_
_processing function_
- processing function that adjusts the initial bounding box, which includes the entire model, to only show individual vines
- processing function which subtracts the height vales from a *solo ground DEM* from a *vine only 3D model* to level the model
- processing function that exports an ortho raster from the side of each vine

_MetashapeProject
- import reference GCPs 

- IRProject.py with class IRProject inheriting from multispectralProject but with other indexes ect

- Add PyExpress Pipelines to PyExpress
- Add a history
#### Documentation
- example work flows / quick start guide
- documentation from Express how to implement PyExpress on MSG, .. or other servers e.g. Grafikrechner, AWS,..




