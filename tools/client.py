
import asyncio

import grpc
import paxos_pb2
import paxos_pb2_grpc
import config
import mylogging
import util
import flags

async def run(iMachineID):
    mylogging.InitLogger()

    oMachineConfig = config.GetConfigByID(iMachineID)
    assert oMachineConfig, "Fail to find paxos[%s] config" % iMachineID

    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.

    sTarget = "%s:%s" % (oMachineConfig.IP(), oMachineConfig.Port())
    mylogging.GetLogger().info("try connect to paxos[%s] %s" % (iMachineID, sTarget))
    async with grpc.aio.insecure_channel(sTarget) as channel:
        stub = paxos_pb2_grpc.PaxosStub(channel)
        oRequest = paxos_pb2.ProposeRequest()
        oRequest = util.PackMsgValue(oRequest, key="name", val=100)
        response = await stub.Propose(oRequest)
    
    mylogging.GetLogger().info("Paxos client received: " + flags.GetResultStr(response.result))

if __name__ == '__main__':
    asyncio.run(run())