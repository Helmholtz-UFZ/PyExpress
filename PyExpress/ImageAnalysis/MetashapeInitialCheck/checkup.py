try:
    import Metashape
    import warnings
except Exception as e:
    print("Some modules are missing {}".format(e))

def metashape_initial_check(version_GUI: str,
                            enable_GPU:  bool,
                            enable_CPU:  bool):

    ''' Checks if the Metashape API and GUI versions are compatible, and if the Metashape API is active.
        Enables GPU and CPU accelaretion as specified in the configuration file.

    *args:
            version_GUI: version number of the locally installed Metashape GUI (e.g., 2.1.2)\n
            enable_GPU: enable GPU acceleration\n
            enable_CPU: enable CPU acceleration if GPU acceleration is enabled

    *raises:
            UserWarning: If the installed GUI and API versions differ.
            UserWarning: If API version is lower then v.2.0.0.
    '''
    
    # enable your GPU for processing and enable CPU if needed / wished
    
    warnings.filterwarnings("once", category=UserWarning)
    
    _APIversion = Metashape.app.version.split('.')
    version_API  = f'{_APIversion[0]}.{_APIversion[1]}.{_APIversion[2]}'
    
    if version_API != version_GUI:
        warnings.warn('GUI and API versions differ. This may cause compatibility issues.'
                      'Ensure both versions match to avoid errors.', UserWarning, stacklevel=2)

    if version_API.startswith('1'):
        warnings.warn('Your Metashape distribution is of version 1.x.y. Some functionalities are not supported here.'
                      'To ensure optimal performance of PyExpress, please upgrade to version 2.0.0 or higher.',
                      UserWarning, stacklevel=2)
        
        input('Continue processing anyway [y,n]?: ')

    if Metashape.app.activated == False:
        warnings.warn('Your Metashape API is not activated yet. This will cause errors.'
                      'Please copy the Metashape license file to your working directory.',
                      UserWarning, stacklevel=2)    
                
        input('Continue processing anyway [y,n]?: ')
    
    print(f'Metashape features: Version API: {Metashape.app.version}\n'
          f"{' ' * 20}Version GUI: {version_GUI}\n"
          f"{' ' * 20}GPU usage:   {enable_GPU} - {len(Metashape.app.enumGPUDevices())} found\n"
          f"{' ' * 20}CPU usage:   {enable_CPU}\n")
    
    if enable_CPU == True:
        Metashape.app.cpu_enable = True
    else:
        Metashape.app.cpu_enable = False
    
    if enable_GPU == True:
        numDevices               = 2**len(Metashape.app.enumGPUDevices())-1
        Metashape.app.gpu_mask   = numDevices
    else:
        Metashape.app.gpu_mask   = -1