# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Initial parameters for applying classification on MS pointclouds.

@author: Martin Kobe, martin.kobe@ufz.de, martin.kobe@email.de

@status: 08.2024; part of the EXPRESS Project (UFZ Leipzig)
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
                
                if paramSet[0]=='test':
                    self.test = getattr(self, paramSet[0])(paramSet=paramSet)

        class vine():
            
            def __init__(self, paramSet=None):         

                if paramSet:
                    self.max_angle = getattr(self, paramSet[1])().max_angle
                    self.max_dist  = getattr(self, paramSet[1])().max_distance
                    self.cell_size = getattr(self, paramSet[1])().cell_size
                
                else:
                    self.max_angle = None
                    self.max_dist  = None
                    self.cell_size = None
                    
            class set1():
                
                def __init__(self):
                    
                    self.max_angle    = 45      # degree
                    self.max_distance = 2       # meter
                    self.cell_size    = 5       # square meter

            class set2():
                
                def __init__(self):
                    
                    self.max_angle    = 0.3     # degree
                    self.max_distance = 0.61    # meter
                    self.cell_size    = 0.61    # square meter

            class set3():
                
                def __init__(self):
                    
                    self.max_angle    = 0.4     # degree
                    self.max_distance = 1.0     # meter
                    self.cell_size    = 1.0     # square meter

            class set4():
                
                def __init__(self):
                    
                    self.max_angle    = 0.2     # degree
                    self.max_distance = 1.0     # meter
                    self.cell_size    = 1.0     # square meter  

        class test():
            
            def __init__(self, paramSet=None):
                    
                if paramSet:
                    self.max_angle = getattr(self, 'testSet')(paramSet[1]).max_angle
                    self.max_dist  = getattr(self, 'testSet')(paramSet[1]).max_distance
                    self.cell_size = getattr(self, 'testSet')(paramSet[1]).cell_size
                
                else:
                    self.max_angle = None
                    self.max_dist  = None
                    self.cell_size = None                    
                    
            class testSet():
                
                def __init__(self, paramSet):
                    
                    self.max_angle    = paramSet['max_angle']    # degree
                    self.max_distance = paramSet['max_distance'] # meter
                    self.cell_size    = paramSet['cell_size']    # square meter

        class crop():
            
            def __init__(self):
                pass