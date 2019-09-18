

def getAccessKey(filePath):
    accessKey = {}
    keyFile = open(filePath, "r", encoding='utf-8-sig')
    lines = keyFile.readlines()

    keyFile.close()
    keys = lines[0].strip().split(",")
    values = lines[1].strip().split(",")

    accessKey[keys[0].strip().replace('"', '')] = values[0].strip().replace('"', '')
    accessKey[keys[1].strip().replace('"', '')] = values[1].strip().replace('"', '')
    return accessKey


#print(returnAccessKey("accessKey.csv"))
