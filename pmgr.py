
import subprocess
import os
import signal
import sys
import asyncio
import importlib

import config
import tools.client as client
import mylogging

PIDINFO_FILENAME = ".pidinfo.txt"
PIDINFO_FILEHEAD = "#writestart"
PIDINFO_FILEEND = "#writeend"

def StartProcesses(iCount):
    iNum = 0
    dProcessInfo =  {}
    for oConfig in config.GetAllConfig():
        iMachineID = oConfig.ID()
        print(iMachineID)
        print("xxxxxxxxxxxx")
        sArgs = f"python.exe start.py {iMachineID}" 
        process = subprocess.Popen(sArgs)
        dProcessInfo[iMachineID] = process.pid

        iNum += 1
        if iNum >= iCount:
            break
    return dProcessInfo

def SaveProcessInfo(dProcessInfo):

    with open(PIDINFO_FILENAME, 'w') as f:
        lstText = []
        lstText.append(PIDINFO_FILEHEAD)
        for iMachineID, pid in dProcessInfo.items():
            lstText.append("%s:%s" % (iMachineID, pid))
        lstText.append(PIDINFO_FILEEND)
        sText = "\n".join(lstText)
        f.write(sText)

def ReadProcessInfo():
    dProcessInfo = {}

    sText = ""
    with open(PIDINFO_FILENAME, 'r') as f:
        sText = f.read()

    if not sText:
       ("%s is empty!" % PIDINFO_FILENAME)
       return dProcessInfo
    
    iStart = sText.find(PIDINFO_FILEHEAD)
    if iStart < 0:
        raise Exception("Fail to find %s in file" % PIDINFO_FILEHEAD)
    iEnd = sText.find(PIDINFO_FILEEND)
    if iEnd < 0:
        raise Exception("Fail to find %s in file" % PIDINFO_FILEEND)
    # NOTE: 不要忘记换行符 "\n"
    iStart += len(PIDINFO_FILEHEAD) + 1
    if iStart >= iEnd:
        mylogging.GetLogger().debug("%s is empty!" % PIDINFO_FILENAME)
        return dProcessInfo
    
    sPIDText = sText[iStart:iEnd]
    lstPIDText = sPIDText.split("\n")

    if not lstPIDText:
        mylogging.GetLogger().debug("%s is empty!" % PIDINFO_FILENAME)
        return dProcessInfo
    
    for sI2PID in lstPIDText:
        if not sI2PID:
            continue
        iMachineID, pid = map(int, sI2PID.split(":"))
        dProcessInfo[iMachineID] = pid
    
    return dProcessInfo

def StopProcesses(dProcessInfo):
    for iMachineID, pid in dProcessInfo.items():
        os.kill(pid, signal.SIGTERM)
        mylogging.GetLogger().debug(f"kill paxos instance {iMachineID} {pid}")

async def main():
    mylogging.InitLogger()
    config.InitConfig()

    mylogging.GetLogger().debug("script name: %s" % sys.argv[0])

    if len(sys.argv) > 1:
        sOperation = sys.argv[1]
        if sOperation == "start":
            if len(sys.argv) > 2:       
                iCount = int(sys.argv[2])
            else:
                iCount = 9999
            dProcessInfo = StartProcesses(iCount)
            mylogging.GetLogger().debug(f"processes: {dProcessInfo}")
            SaveProcessInfo(dProcessInfo)
        elif sOperation == "stop":
            dProcessInfo = ReadProcessInfo()
            mylogging.GetLogger().debug(f"processes: {dProcessInfo}")
            StopProcesses(dProcessInfo)
            SaveProcessInfo({})
        elif sOperation == "propose":
            iMachineID = int(sys.argv[2])
            await client.run(iMachineID)
        elif sOperation == "reload":
            sModuleName = sys.argv[2]
            importlib.reload(importlib.import_module(sModuleName))
            mylogging.GetLogger().info(f"reload {sModuleName}")
    else:
        raise Exception("parameter error")

if __name__ == "__main__":
    asyncio.run(main())
