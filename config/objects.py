
class CMachineConfig(object):

    def __init__(self, dConfig) -> None:
        self.m_Config = dConfig

    def ID(self):
        return self.m_Config["ID"]
    
    def Name(self):
        return self.m_Config["Name"]
    
    def IP(self):
        return self.m_Config["IP"]
    
    def Port(self):
        return self.m_Config["Port"]

