from aliyunsdkcore.client import AcsClient
from helpers import getAccessKey

from postgres import backupDatabase
from postgres import listBackUps
from postgres import restoreDatabase
from postgres import cloneInstance
from postgres import createTemporaryInstance
from postgres import viewBackupPolicy
from postgres import setBackupTime
from postgres import deleteBackup

import sys
import time
import json

def main():
    accessKeyFilePath = sys.argv[1]
    accessKey = getAccessKey(accessKeyFilePath)
    REGION_ID = "cn-shanghai"
    client = AcsClient(accessKey["AccessKeyId"], accessKey["AccessKeySecret"], REGION_ID)

    if sys.argv[2] == "restore-instance":
        dbInstanceId = sys.argv[3]
        backupId = sys.argv[4]
        response = restoreDatabase(client, dbInstanceId, backupId)
        if response is None:
            print("Restore failed.")
        else:
            print("Restore successfull.")

    elif sys.argv[2] == "backup-instance":
        dbInstanceId = sys.argv[3]
        response = backupDatabase(client, dbInstanceId)
        if response is None:
            print("Backup failed.")
        else:
            print("Backup successful.")

    elif sys.argv[2] == "list-backups":
        instanceId = sys.argv[3]
        startTime = sys.argv[4]
        endTime = sys.argv[5]
        response = listBackUps(client, instanceId, startTime, endTime)
        if response:
            print("List of Backups for Database InstanceId {}: ".format(instanceId))
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "clone-instance":
        instanceId = sys.argv[3]
        restoreTime = sys.argv[4]
        response = cloneInstance(client, instanceId, restoreTime)
        if response:
            print("Clone of Database instance was successful.")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "create-temporary-instance":
        instanceId = sys.argv[3]
        backupId = sys.argv[4]
        restoreTime = sys.argv[5]
        response = createTemporaryInstance(client, instanceId, backupId, restoreTime)
        if response:
            print("Temporary instance creation was successful.")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "view-backup-policy":
        instanceId = sys.argv[3]
        policy = sys.argv[4]
        policyMode = None
        if policy == "data":
            policyMode = "DataBackupPolicy"
        else:
            policyMode = "LogBackupPolicy"
        response = viewBackupPolicy(client, instanceId, policyMode)
        if response:
            print("Clone of Database instance was successful.")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "set-backup-time":
        instanceId = sys.argv[3]
        backupTime = sys.argv[4]
        response = setBackupTime(client, instanceId, backupTime)
        if response:
            print("Clone of Database instance was successful.")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "delete-backup":
        instanceId = sys.argv[3]
        backupId = sys.argv[4]
        response = deleteBackup(client, instanceId, backupId)
        if response:
            print("Backup with id = {} deleted successfully.".format(backupId))
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
