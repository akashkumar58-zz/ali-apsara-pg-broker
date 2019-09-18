from aliyunsdkcore.client import AcsClient
from helpers import getAccessKey

from postgres import createInstance
from postgres import createInitialAccount
from postgres import createDatabase
from postgres import bindService
from postgres import unbindService
from postgres import deleteInstance

from postgres import changeMaintenanceWindowPeriod
from postgres import checkInstanceStatus
from postgres import instanceCreationTime
from postgres import describeRegions
from postgres import migrateZone
from postgres import upgradeVersion

import sys
import json
import uuid


def help():
    print("Usage: python3 {} <accessKeyFilePath> <create-instance/delete-instance/bind-service/unbind-service> [options]".format(sys.argv[0]))
    print("create-instance: Default network type is classic. If you want to create instance in VPC provide VPCId and VSwitchId separated by space after create-instance.")
    print("delete-instance: Provide DBInstanceId of the instance which you want to delete.")
    print("bind-service: host port master-account-username master-account-password databaseName")
    print("unbind-service: host port master-account-username master-account-password databaseName user-created-while-bind")
    return

def main():
    if len(sys.argv) < 3:
        help()
        sys.exit(1)

    accessKeyFilePath = sys.argv[1]
    accessKey = getAccessKey(accessKeyFilePath)
    REGION_ID = "eu-central-1"   #cn-shanghai
    client = AcsClient(accessKey["AccessKeyId"], accessKey["AccessKeySecret"], REGION_ID)

    if sys.argv[2] == "describe-region":
        response = describeRegions(client)
        if response is None:
            print("Could not describe regions.")
        else:
            jsonResponse = json.loads(response.decode("utf-8"))
            print("Response of describe regions is as follows: ")
            print(json.dumps(jsonResponse, indent=4, sort_keys=True))


    if sys.argv[2] == "create-instance":
        vpcNet = False
        vpcId = None
        vSwitchId = None

        if len(sys.argv) == 5:
            vpcNet = True
            vpcId = sys.argv[3]
            vSwitchId = sys.argv[4]

        elif len(sys.argv) > 3 and len(sys.argv) < 5:
            help()
            sys.exit(1)
        import time
        startTime = time.time()
        response = createInstance(client, vpcNet, vpcId, vSwitchId)
        endTime = time.time()
        print("API call for instance creation took {:f} seconds.".format(endTime - startTime))
        if response is not None:
            jsonResponse = json.loads(response.decode("utf-8"))
            print("Response of DB instace creation is as follows: ")
            print(json.dumps(jsonResponse, indent=4, sort_keys=True))
        else:
            print("Database instance creation failed !!!")

    elif sys.argv[2] == "delete-instance":
        if len(sys.argv) < 4:
            help()
            sys.exit(1)
        else:
            dbInstanceId = sys.argv[3]
            import time
            startTime = time.time()
            response = deleteInstance(client, dbInstanceId)
            endTime = time.time()
            print("API call for instance deletion took {:f} seconds.".format(endTime - startTime))
            if response is None:
                print("Database instance {} deletion failed!!!".format(dbInstanceId))
            else:
                print("Database instance having DBInstanceId got deleted successfully.".format(dbInstanceId))
                print(json.dumps(json.loads(response.decode("utf-8")), indent=4, sort_keys=True))

    elif sys.argv[2] == "check-instance-status":
        dbInstanceId = sys.argv[3]
        response = instanceCreationTime(client, dbInstanceId)

    elif sys.argv[2] == "create-initial-account":
        dbInstanceId = sys.argv[3]
        userName = "postgres_user"
        password = "Postgres_user"
        if len(sys.argv) > 4:
            userName = sys.argv[4]
            password = sys.argv[5]
        import time
        startTime = time.time()
        response = createInitialAccount(client, dbInstanceId, userName, password)
        endTime = time.time()
        print("API call for account creation took {:f} seconds.".format(endTime - startTime))
        if response is None:
            print("Account creation for database instance {} failed!!!".format(dbInstanceId))
        else:
            print("Initial account with user {} and password {} created successfully for database instance.".format(userName, password, dbInstanceId))
            print(json.dumps(json.loads(response.decode("utf-8")), indent=4, sort_keys=True))

    elif sys.argv[2] == "create-database":
        host = sys.argv[3]
        port = 3433
        dbName = uuid.uuid4().hex
        user = "postgres_user"
        password= "Postgres_user"
        if len(sys.argv) > 4:
            port = sys.argv[4]
            user = sys.argv[5]
            password = sys.argv[6]
            dbName = sys.argv[7]

        import time
        startTime = time.time()
        response = createDatabase(host, port, user, password, dbName)
        endTime = time.time()
        print("Database creation took {:f} seconds.".format(endTime - startTime))
        if response is False:
            print("Database {} creation failed!!!".format(dbName))
        else:
            print("Database {} created successfully for database instance.".format(dbName))

    elif sys.argv[2] == "bind-service":
        host = sys.argv[3]
        port = sys.argv[4]
        userName = sys.argv[5]
        password = sys.argv[6]
        dbName = sys.argv[7]
        response = bindService(host, port, userName, password, dbName)
        if len(response) > 0:
            print("Binding successfull. Bind credentials:")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))
        else:
            print("Binding was unsuccessfull.")

    elif sys.argv[2] == "unbind-service":
        host = sys.argv[3]
        port = sys.argv[4]
        userName = sys.argv[5]
        password = sys.argv[6]
        dbName = sys.argv[7]
        userToDelete = sys.argv[8]
        response = unbindService(host, port, userName, password, dbName, userToDelete)
        if response:
            print("Unbind Seccessfull.")
        else:
            print("Error: Unbind failed.")

    elif sys.argv[2] == "configure-maintenance-time":
        instanceId = sys.argv[3]
        time = sys.argv[4]
        response = changeMaintenanceWindowPeriod(client, instanceId, time)
        if response:
            print("Maintenance period changed successfully.")

    elif sys.argv[2] == "migrate-zone":
        instanceId = sys.argv[3]
        zoneId = sys.argv[4]
        switchId = sys.argv[5]
        response = migrateZone(client, instanceId, zoneId, switchId)
        if response:
            print("Migration of database was successful.")

    elif sys.argv[2] == "upgrade-version":
        instanceId = sys.argv[3]
        engineVersion = sys.argv[4]
        response = upgradeVersion(client, instanceId, engineVersion)
        if response:
            print("Database engine version upgraded successfully.")

    else:
        help()
    return


if __name__ == "__main__":
    main()

