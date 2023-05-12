
from . import machineinfo
from . import objects

import mylogging

if "g_MachineID" not in globals():
    g_MachineID = -9999

if "g_MachineConfig" not in globals():
    g_MachineConfig = {}

def LoadConfig():
    global g_MachineConfig

    g_MachineConfig = {}
    for dConfig in machineinfo.MACHINE_INFO:
        iMachineID = dConfig["ID"]
        oConfig = objects.CMachineConfig(dConfig)
        g_MachineConfig[iMachineID] = oConfig
        mylogging.GetLogger().info("load machine config %s %s %s" % (iMachineID, oConfig.IP(), oConfig.Port()))

def SetMachineID(iMachineID):
    global g_MachineID
    mylogging.GetLogger().info("set machine id from %s to %s" % (g_MachineID, iMachineID))
    g_MachineID = iMachineID

def GetConfigByID(iID):
    global g_MachineConfig
    return g_MachineConfig.get(iID, None)

def GetAllConfig():
    global g_MachineConfig
    return g_MachineConfig.values()

def GetMyConfig():
    global g_MachineID
    return GetConfigByID(g_MachineID)

def InitConfig(iMachineID=0):
    LoadConfig()
    if iMachineID:
        SetMachineID(iMachineID)    