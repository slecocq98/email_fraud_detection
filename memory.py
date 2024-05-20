class Memory:
    __instance = None
    model_deployed = None
    model_deployed_id = None

    @staticmethod
    def getInstance():
        """
        Get the permanent state of the memory. <br/>
        :return:
        """
        if Memory.__instance is None:
            Memory()
        return Memory.__instance

    def __init__(self):
        """
        Virtual private Constructor
        """
        if Memory.__instance is not None:
            raise Exception("This class is a singleton !")
        else:
            Memory.__instance = self
