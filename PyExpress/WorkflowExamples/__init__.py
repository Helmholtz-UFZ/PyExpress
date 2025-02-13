# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

try:
    from .StereoProject.MakoG319_workflow import *
    from .DroneProject.M2EA_workflow      import *
    from .DroneProject.M3T_workflow       import *
except:
    pass

from .DroneProject.TEST_workflow import *