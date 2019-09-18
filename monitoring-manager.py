from aliyunsdkcore.client import AcsClient
from helpers import getAccessKey

from postgres import getResourceUsage
from postgres import setMonitoringPeriod
from postgres import getPerformanceUsage

import sys
import json

def main():
    accessKeyFilePath = sys.argv[1]
    accessKey = getAccessKey(accessKeyFilePath)
    REGION_ID = "cn-shanghai"
    client = AcsClient(accessKey["AccessKeyId"], accessKey["AccessKeySecret"], REGION_ID)

    if sys.argv[2] == "list-resource-usage":
        dbInstanceId = sys.argv[3]
        response = getResourceUsage(client, dbInstanceId)
        if response:
            print("Resource usage for database instance:")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    elif sys.argv[2] == "set-monitoring-period":
        dbInstanceId = sys.argv[3]
        period = sys.argv[4]
        response = setMonitoringPeriod(client, dbInstanceId, period)
        if response:
            print("Monitoring period was set to {} seconds successfully.".format(period))

    elif sys.argv[2] == "get-performance-usage":
        dbInstanceId = sys.argv[3]
        startTime = sys.argv[4]
        endTime = sys.argv[5]
        response = getPerformanceUsage(client, dbInstanceId, startTime, endTime)
        if response:
            print("Performance parameters of database instance: ")
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))

    else:
        pass


if __name__ == "__main__":
    main()
