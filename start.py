
import asyncio

import sys
import os

import grpc
import config
import mylogging
import servicer

def InitDiretory():
    if not os.path.exists("log"):
        os.makedirs("log")

def LoadConfig():
    pass

async def InitServer(oMachineConfig):
    server = grpc.aio.server()
    servicer.AddServicer(server)
    sListenAddr = '[::]:' + oMachineConfig.Port()
    server.add_insecure_port(sListenAddr)
    await server.start()
    mylogging.GetLogger().info("Paxos[%s] started, listening on %s" % (oMachineConfig.ID(), oMachineConfig.Port()))
    await server.wait_for_termination()

async def Start(iMachineID):
    InitDiretory()
    mylogging.InitLogger()
    config.InitConfig(iMachineID)
    
    oMachineConfig = config.GetConfigByID(iMachineID)
    assert oMachineConfig, "Fail to find machine config by ID[%s]" % iMachineID

    await InitServer(oMachineConfig)

async def main():
    if len(sys.argv) > 1:
        iMachineID = int(sys.argv[1])
        await Start(iMachineID)
    else:
        raise Exception("没有传入 paxos 机器编号")

if __name__ == "__main__":
    asyncio.run(main())

"""
备忘：
1. 命令行参数: click
2. grpc: tutorial
3. aysnc await
4. logging
5. reload
6. git 管理
"""
