from aliyunsdkcore.client import AcsClient
from helpers import getAccessKey

from postgres import getErrorLogs
from postgres import getSlowLogDetails
from postgres import querySQLAuditLogs
from postgres import enableSqlCollectorPolicy

import sys
import json

def main():
    accessKeyFilePath = sys.argv[1]
    accessKey = getAccessKey(accessKeyFilePath)
    REGION_ID = "cn-shanghai"
    client = AcsClient(accessKey["AccessKeyId"], accessKey["AccessKeySecret"], REGION_ID)

    if sys.argv[2] == "list-error-logs":
        dbInstanceId = sys.argv[3]
        startTime = sys.argv[4]
        endTime = sys.argv[5]
        response = getErrorLogs(client, dbInstanceId, startTime, endTime)
        if response:
            print("Error logs: ")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "slow-log-details":
        dbInstanceId = sys.argv[3]
        startTime = sys.argv[4]
        endTime = sys.argv[5]
        dbName = sys.argv[6]
        response = getSlowLogDetails(client, dbInstanceId, startTime, endTime, dbName)
        if response:
            print("Slow log details for database {} is as follows:".format(dbName))
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "audit-logs":
        dbInstanceId = sys.argv[3]
        startTime = sys.argv[4]
        endTime = sys.argv[5]
        dbName = sys.argv[6]
        response = querySQLAuditLogs(client, dbInstanceId, startTime, endTime, dbName)
        if response:
            print("Audit logs for database {} is as follows:".format(dbName))
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "enable-sql-collector":
        dbInstanceId = sys.argv[3]
        response = enableSqlCollectorPolicy(client, dbInstanceId)
        if response:
            print("SQLCollector policy for database {} was successful.".format(dbInstanceId))

    else:
        pass


if __name__ == "__main__":
    main()
