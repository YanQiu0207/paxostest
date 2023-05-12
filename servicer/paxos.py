
import asyncio
import functools

import grpc
import paxos_pb2
import paxos_pb2_grpc

import mylogging
import util
import config
import flags

class CPropose(paxos_pb2_grpc.PaxosServicer):

    async def Propose(
        self,
        request: paxos_pb2.ProposeRequest,
        context: grpc.aio.ServicerContext) -> paxos_pb2.ProposeReply:
        key = util.UnPackMsgValue(request, "key")
        val = util.UnPackMsgValue(request, "val")
        mylogging.GetLogger().debug("request: key=%s, val=%s" % (key, val))

        oProposer = CProposer(key, val)
        iResult = await oProposer.Run()

        return paxos_pb2.ProposeReply(result=iResult)
    
    def Prepare(
            self,
            request: paxos_pb2.PrepareRequest,
            context: grpc.aio.ServicerContext) -> paxos_pb2.PrepareReply:
        key = util.UnPackMsgValue(request, "key")
        
        oAcceptor = GetOrNewAcceptor(key)
        iResult, maxbal, maxval = oAcceptor.OnPrepare(request.bal)
        
        response = paxos_pb2.PrepareReply()
        util.PackMsgValue(response, key=key)
        response.result = iResult
        response.maxbal = maxbal
        util.PackMsgValue(response, maxval=maxval)
        return response

    def Accept(
            self,
            request: paxos_pb2.AcceptRequest,
            context: grpc.aio.ServicerContext) -> paxos_pb2.AcceptReply:
        key = util.UnPackMsgValue(request, "key")
        bal = request.bal
        val = util.UnPackMsgValue(request, "val")
        
        oAcceptor = GetOrNewAcceptor(key)
        iResult = oAcceptor.OnAccept(bal, val)

        response = paxos_pb2.AcceptReply()
        util.PackMsgValue(response, key=key)
        response.result = iResult
        response.maxbal = oAcceptor.MaxAcceptBal()
        return response

class CProposer(object):

    def __init__(self, key, val) -> None:
        self.m_Bal = 1
        self.m_InstanceID = key
        self.m_Value = val

    async def Run(self):
        lstConfig = config.GetAllConfig()
        if not lstConfig:
            mylogging.GetLogger().debug("Fail to find Acceptor")
            return flags.RESULT_FAIL
        iAcceptorNum = len(lstConfig)
        iNeedNum = iAcceptorNum // 2 + 1
        mylogging.GetLogger().debug(f"P1a servernum {iAcceptorNum} {iNeedNum}")
        
        lstResult = await self.BroadcastRequest(lstConfig, self.SendPrepareRequest)
        mylogging.GetLogger().info("P1b response num %s" % len(lstResult))
        if not lstResult or len(lstResult) < iNeedNum:
            return flags.RESULT_FAIL
        
        iPrepareCnt = 0
        iEmptyResNum = 0
        maxbal, maxval = None, None
        for iMachineID, response in lstResult:
            bExec = True if response else False
            mylogging.GetLogger().debug("P1b recv result key %s machine %s exec %s" % (self.m_InstanceID, iMachineID, bExec))
            if not response:
                iEmptyResNum += 1
                continue
            key = util.UnPackMsgValue(response, "key")
            res_maxbal = response.maxbal
            res_maxval = util.UnPackMsgValue(response, "maxval")
            mylogging.GetLogger().debug("P1b vote result %s %s %s %s %s" % (iMachineID, key, flags.GetResultStr(response.result), res_maxbal, res_maxval))
            if key != self.m_InstanceID:
                mylogging.GetLogger().error("P1b error instanceid %s %s" % (key, self.m_InstanceID))
                continue
            if not maxbal or res_maxbal > maxbal:
                maxbal, maxval = res_maxbal, res_maxval
            if response.result != flags.RESULT_SUCCESS:
                mylogging.GetLogger().debug("P1b vote fail %s %s" % (iMachineID, key))
                continue
            mylogging.GetLogger().debug("P1b vote ok %s %s" % (iMachineID, key))
            iPrepareCnt += 1
            if iPrepareCnt >= iNeedNum:
                break
        
        mylogging.GetLogger().debug("P1b vote stat %s %s %s %s %s" % (key, iNeedNum, iPrepareCnt, maxbal, maxval))
        if iPrepareCnt < iNeedNum:
            # NOTE: 存活机器数量不足，提前退出，否则提升提案编号后重试
            if len(lstResult) - iEmptyResNum < iNeedNum:
                return flags.RESULT_FAIL
            # NOTE: 真实系统中，应该随机等待一段时间后再重试
            if maxbal and maxbal >= self.m_Bal:
                self.m_Bal = maxbal + 1
            else:
                self.m_Bal += 1
            return await self.Run()
        
        iAcceptVal = self.m_Value
        if maxbal:
            iAcceptVal = maxval

        mylogging.GetLogger().info("P2a request %s %s %s" % (self.m_InstanceID, self.m_Bal, iAcceptVal))
        cbfunc = functools.partial(self.SendAcceptRequest, self.m_InstanceID, self.m_Bal, iAcceptVal)
        lstResult = await self.BroadcastRequest(lstConfig, cbfunc)
        mylogging.GetLogger().info("P2b response num %s" % len(lstResult))

        iAcceptCnt = 0
        for iMachineID, response in lstResult:
            if not response:
                continue
            key = util.UnPackMsgValue(response, "key")
            if key != self.m_InstanceID:
                mylogging.GetLogger().debug("P2b error instanceid %s %s" % (key, self.m_InstanceID))
                continue
            if response.result != flags.RESULT_SUCCESS:
                mylogging.GetLogger().debug("P2b vote fail %s %s" % (iMachineID, key))
                continue
            iAcceptCnt += 1
            if iAcceptCnt >= iNeedNum:
                break
        if iAcceptCnt < iNeedNum:
            mylogging.GetLogger().debug("P2b vote fail %s %s %s" % (key, iNeedNum, iAcceptCnt))
            return flags.RESULT_UNKNOWN
        mylogging.GetLogger().debug("P2b vote ok %s %s %s" % (key, iNeedNum, iAcceptCnt))
        return flags.RESULT_SUCCESS
        
    async def BroadcastRequest(self, lstConfig, cbfunc):
        lstTask = []
        for oConfig in lstConfig:
            oTask = asyncio.create_task(cbfunc(oConfig))
            lstTask.append(oTask)
        lstDonTask, _ = await asyncio.wait(lstTask)
        lstResult = []
        for oTask in lstDonTask:
            lstResult.append(oTask.result())
        return lstResult

    async def SendPrepareRequest(self, oConfig):
        sTargetAddr = "%s:%s" % (oConfig.IP(), oConfig.Port())
        async with grpc.aio.insecure_channel(sTargetAddr) as channel:
            request = paxos_pb2.PrepareRequest()
            util.PackMsgValue(request, key=self.m_InstanceID)
            request.bal = self.m_Bal
            
            stub = paxos_pb2_grpc.PaxosStub(channel)
            try:
                response = await stub.Prepare(request, timeout=10)
            except Exception as e:
                mylogging.GetLogger().warn("P1a prepare error %s %s" % (oConfig.ID(), e))
                response = None
            return (oConfig.ID(), response)
        
    async def SendAcceptRequest(self, key, bal, val, oConfig):
        sTargetAddr = "%s:%s" % (oConfig.IP(), oConfig.Port())
        async with grpc.aio.insecure_channel(sTargetAddr) as channel:
            request = paxos_pb2.AcceptRequest()
            util.PackMsgValue(request, key=key, val=val)
            request.bal = bal
            
            stub = paxos_pb2_grpc.PaxosStub(channel)
            try:
                response = await stub.Accept(request, timeout=10)
            except Exception as e:
                mylogging.GetLogger().warn("P2a accept error %s %s" % (oConfig.ID(), e))
                response = None
            return (oConfig.ID(), response)

class CAcceptor(object):

    def __init__(self, key):
        self.m_InstanceID = key
        self.m_PrepareBal = 0
        self.m_MaxAcceptBal = 0
        self.m_MaxAcceptVal = 0

    def InstanceID(self):
        return self.m_InstanceID
    
    def PrepareBal(self):
        return self.m_PrepareBal
    
    def MaxAcceptBal(self):
        return self.m_MaxAcceptBal
    
    def MaxAcceptVal(self):
        return self.m_MaxAcceptVal

    def OnPrepare(self, bal):
        if bal > self.m_PrepareBal:
            # TODO: 存盘 2023-05-02 [tesla]
            mylogging.GetLogger().info("P1a ok %s %s %s" % (self.m_InstanceID, self.m_PrepareBal, bal))
            self.m_PrepareBal = bal
            return flags.RESULT_SUCCESS, self.m_MaxAcceptBal, self.m_MaxAcceptVal
        mylogging.GetLogger().info("P1a fail %s %s %s" % (self.m_InstanceID, self.m_PrepareBal, bal))
        return flags.RESULT_FAIL, self.m_MaxAcceptBal, self.m_MaxAcceptVal

    def OnAccept(self, bal, val):
        if bal >= self.m_PrepareBal:
            # TODO: 存盘 2023-05-02 [tesla]
            mylogging.GetLogger().info("P2b ok %s %s %s %s" % (self.m_InstanceID, self.m_PrepareBal, bal, val))
            self.m_PrepareBal, self.m_MaxAcceptBal, self.m_MaxAcceptVal = bal, bal, val
            return flags.RESULT_SUCCESS
        mylogging.GetLogger().info("P2b fail %s %s %s %s" % (self.m_InstanceID, self.m_PrepareBal, bal, val))
        return flags.RESULT_FAIL

if "g_Acceptor" not in globals():
    g_Acceptor = {}

def GetOrNewAcceptor(key):
    if key in g_Acceptor:
        return g_Acceptor[key]
    obj = CAcceptor(key)
    g_Acceptor[key] = obj
    return obj
    
def AddServicer(server):
    paxos_pb2_grpc.add_PaxosServicer_to_server(CPropose(), server)

"""
优化：
1. 不需要等待所有的都返回，只有有大多数成功返回就可以了；Accept 时可以选取 prepare 成功的机器
2. 支持读取操作
3. 基于 Basic Paxos 实现多个值，单个值多次达成共识
"""