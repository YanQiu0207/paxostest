
RESULT_FAIL = 0
RESULT_SUCCESS = 1
RESULT_UNKNOWN = 2

def GetResultStr(iResult):
    if iResult == RESULT_FAIL:
        return "Fail"
    elif iResult == RESULT_SUCCESS:
        return "Success"
    else:
        return "Unknown"