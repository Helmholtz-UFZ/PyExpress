# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Initial parameters for applying classification on MS pointclouds.

@author: Martin Kobe, martin.kobe@ufz.de, martin.kobe@email.de

@status: 12.2025; part of the EXPRESS Project (UFZ Leipzig)


# parametrization for point classification includes, dependent on the case, the main parameters:
#
# (a) max_angle [degree; default: 15°]
#   → Maximum tilt a point may have relative to the local ground surface to still be classified as ground.
#   → Controls sensitivity to slopes.
#
# (b) max_distance [meters; default: 1.0m]
#   → Maximum vertical distance a point may deviate from the ground model to remain ground.
#   → Separates ground from vegetation/objects.
#
# (c) cell_size [square meters; default: 50.0m]
#   → Grid cell size used to build the local ground reference surface.
#   → Controls smoothing and spatial resolution.
#
# (d) erosion_radius [meters; default: 0.0m]
#   → Radius (meters) used to erode small protrusions (stems, small objects) in the ground model.
#   → Makes the ground model more robust to vegetation.

"""

class Parameters():
    
    def __init__(self, paramSet=None):

        self.Classification = self.Classification(paramSet) 
    
    class Classification():
        
        def __init__(self, paramSet=None, testParamSet=None):
            
            if paramSet:

                if paramSet[0]=='vine':
                    self.vine = getattr(self, paramSet[0])(paramSet=paramSet)
                
                if paramSet[0]=='crop':
                    self.crop = getattr(self, paramSet[0])(paramSet=paramSet)
                   
                if paramSet[0]=='fruit':
                    self.crop = getattr(self, paramSet[0])(paramSet=paramSet)
                
                if paramSet[0]=='test':
                    self.test = getattr(self, paramSet[0])(paramSet=paramSet)

        class vine():
            
            '''vineyard specific'''

            def __init__(self, paramSet=None):         

                if paramSet:
                    self.max_angle      = getattr(self, paramSet[1])().max_angle
                    self.max_dist       = getattr(self, paramSet[1])().max_distance
                    self.cell_size      = getattr(self, paramSet[1])().cell_size
                    self.erosion_radius = 0.0
                    
                else:
                    self.max_angle      = 15    # default
                    self.max_dist       = 1.0   # default
                    self.cell_size      = 50.0  # default
                    self.erosion_radius = 0.0   # default
                                        
            class set1():
                
                def __init__(self):
                    
                    self.max_angle    = 45      # degree
                    self.max_distance = 2       # meter
                    self.cell_size    = 5       # meter

            class set2():
                
                def __init__(self):
                    
                    self.max_angle    = 0.3     # degree
                    self.max_distance = 0.61    # meter
                    self.cell_size    = 0.61    # meter

            class set3():
                
                def __init__(self):
                    
                    self.max_angle    = 0.4     # degree
                    self.max_distance = 1.0     # meter
                    self.cell_size    = 1.0     # meter

            class set4():
                
                def __init__(self):
                    
                    self.max_angle    = 0.2     # degree
                    self.max_distance = 1.0     # meter
                    self.cell_size    = 1.0     # meter  
               
        class fruit():
            
            '''specific for plantagion of fruit trees'''            

            def __init__(self, paramSet=None):         

                if paramSet:
                    self.max_angle      = getattr(self, paramSet[1])().max_angle
                    self.max_dist       = getattr(self, paramSet[1])().max_distance
                    self.cell_size      = getattr(self, paramSet[1])().cell_size
                    self.erosion_radius = getattr(self, paramSet[1])().erosion_radius
                
                else:
                    self.max_angle      = 15    # default
                    self.max_dist       = 1.0   # default
                    self.cell_size      = 50.0  # default
                    self.erosion_radius = 0.0   # default
                    
            class set1():
                
                def __init__(self):
                    
                    self.max_angle      = 15     # degree
                    self.max_distance   = 0.3    # meter
                    self.cell_size      = 0.8    # meter
                    self.erosion_radius = 0.5    # meter

            class set2():
                
                def __init__(self):
                    
                    self.max_angle      = 15     # degree
                    self.max_distance   = 0.4    # meter
                    self.cell_size      = 1.0    # meter
                    self.erosion_radius = 0.3    # meter

            class set3():
                
                def __init__(self):
                    
                    self.max_angle      = 10     # degree
                    self.max_distance   = 0.25   # meter
                    self.cell_size      = 0.7    # meter
                    self.erosion_radius = 0.4    # meter

            class set4():
                
                def __init__(self):
                    
                    self.max_angle      = 8      # degree
                    self.max_distance   = 0.2    # meter
                    self.cell_size      = 0.6    # meter
                    self.erosion_radius = 0.6    # meter
                    
        class crop():
            
            '''specific for crops/croplands such as meadow, grassland, corn'''
            
            def __init__(self):
                pass
                
        class test():
            
            def __init__(self, paramSet=None):
                    
                if paramSet:
                    self.max_angle      = getattr(self, 'testSet')(paramSet[1]).max_angle
                    self.max_dist       = getattr(self, 'testSet')(paramSet[1]).max_distance
                    self.cell_size      = getattr(self, 'testSet')(paramSet[1]).cell_size
                    self.erosion_radius = getattr(self, paramSet[1])().erosion_radius
                
                else:
                    self.max_angle      = 15    # default
                    self.max_dist       = 1.0   # default
                    self.cell_size      = 50.0  # default
                    self.erosion_radius = 0.0   # default            
                    
            class testSet():
                
                def __init__(self, paramSet):
                    
                    self.max_angle      = paramSet['max_angle']      # degree
                    self.max_distance   = paramSet['max_distance']   # meter
                    self.cell_size      = paramSet['cell_size']      # meter
                    self.erosion_radius = paramSet['erosion_radius'] # meter