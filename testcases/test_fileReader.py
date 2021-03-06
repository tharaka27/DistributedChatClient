from utilities.fileReader import FileReader

def test():
    f = FileReader()
    config_objects = f.populate("configuration.txt")

    for obj in config_objects:
        s_name = obj.getServerName()
        s_add = obj.getAddress()
        s_client_port = obj.getClientPort()
        s_cord_port = obj.getCoordinationPort()

        print("==================================================")
        print("Server name -> ",s_name)
        print("Server address -> ",s_add)
        print("Server client port -> ",s_client_port)
        print("Server coordinator port -> ",s_cord_port)
        print("==================================================\n")