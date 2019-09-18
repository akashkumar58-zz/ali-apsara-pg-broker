from helpers import getAccessKey
import time
import uuid
import json
import random
import string
import psycopg2
from psycopg2 import DatabaseError

# Alibaba Cloud SDK exception import
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException

# Instance management Request Imports
from aliyunsdkrds.request.v20140815 import CreateDBInstanceRequest
from aliyunsdkrds.request.v20140815 import DeleteDBInstanceRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstanceAttributeRequest
from aliyunsdkrds.request.v20140815 import ModifyDBInstanceMaintainTimeRequest
from aliyunsdkrds.request.v20140815 import MigrateToOtherZoneRequest
from aliyunsdkrds.request.v20140815 import UpgradeDBInstanceEngineVersionRequest

# Database account related import
from aliyunsdkrds.request.v20140815 import CreateAccountRequest

# Backup and Recovery related imports
from aliyunsdkrds.request.v20140815 import CreateBackupRequest
from aliyunsdkrds.request.v20140815 import RestoreDBInstanceRequest
from aliyunsdkrds.request.v20140815 import DescribeBackupsRequest
from aliyunsdkrds.request.v20140815 import CloneDBInstanceRequest
from aliyunsdkrds.request.v20140815 import CreateTempDBInstanceRequest
from aliyunsdkrds.request.v20140815 import DescribeBackupPolicyRequest
from aliyunsdkrds.request.v20140815 import ModifyBackupPolicyRequest
from aliyunsdkrds.request.v20140815 import DeleteBackupRequest

# Logs related imports
from aliyunsdkrds.request.v20140815 import DescribeErrorLogsRequest
from aliyunsdkrds.request.v20140815 import DescribeSlowLogRecordsRequest
from aliyunsdkrds.request.v20140815 import DescribeSQLLogRecordsRequest
from aliyunsdkrds.request.v20140815 import ModifySQLCollectorPolicyRequest

# Monitoring related imports
from aliyunsdkrds.request.v20140815 import DescribeResourceUsageRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancePerformanceRequest

# Miscellaneous imports
from aliyunsdkrds.request.v20140815 import DescribeRegionsRequest
from aliyunsdkrds.request.v20140815 import ModifyDBInstanceMonitorRequest

###################################################################################################
################################## Instance management functions ##################################
###################################################################################################
def createInstance(client, vpcNet=False, vpcId=None, vSwitchId=None):
    # Creating request object
    request = CreateDBInstanceRequest.CreateDBInstanceRequest()
    # Setting request parameters
    request.set_Engine("PostgreSQL")
    request.set_EngineVersion("9.4")
    request.set_DBInstanceClass("rds.pg.t1.small")
    request.set_DBInstanceStorage(5)       # Storage space in GB, it can increase progressively at a rate of 5 GB
    request.set_DBInstanceNetType("Intranet")
    request.set_SecurityIPList("0.0.0.0/0")
    request.set_PayType("Postpaid")
    request.set_ClientToken(uuid.uuid4().hex)
    request.set_ZoneId("cn-shanghai-MAZ1(b,c)")
    if vpcNet:
        request.set_InstanceNetworkType("VPC")
        request.set_VPCId(vpcId)
        request.set_VSwitchId(vSwitchId)
        #request.set_PrivateIpAddress("192.168.77.29")
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while creating DB instance.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def deleteInstance(client, instanceId):
    # Creating request object
    request = DeleteDBInstanceRequest.DeleteDBInstanceRequest()
    # Setting request parameters
    request.set_DBInstanceId(instanceId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while deleting DB instance.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


# Database Initial Account management functions
def createInitialAccount(client, instanceId, accountName, accountPassword):
    # Creating request object
    request = CreateAccountRequest.CreateAccountRequest()
    # Setting request parameters
    request.set_DBInstanceId(instanceId)
    request.set_AccountName(accountName)
    request.set_AccountPassword(accountPassword)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while creating initial account.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None

# Functions related to cloudfoundry(bind, unbind) and it's helpers(create-database)
def createDatabase(host, port, accountName, accountPassword, dbName):
    connectionString = "host={} port={} dbname={} user={} password={}".format(host, port, "postgres", accountName, accountPassword)
    success = False
    connection = None
    try:
        connection = psycopg2.connect(connectionString)
        connection.autocommit = True
        cur = connection.cursor()
        cur.execute("CREATE DATABASE \"%s\" ;" % dbName)
        print("Database {} created successfully.")
        success = True
        cur.close()
    except DatabaseError as error:
        if connection:
            connection.rollback()
            print("Database creation failed with error:  %s" % error)
    finally:
        if connection:
            connection.close()
    return success


def bindService(host, port, accountName, accountPassword, dbName):
    connectionString = "host={} port={} dbname={} user={} password={}".format(host, port, dbName, accountName, accountPassword)
    credentials = {}
    try:
        connection = psycopg2.connect(connectionString)
        connection.autocommit = True
        cur = connection.cursor()
        cur.execute("SELECT COUNT(rolname) from pg_catalog.pg_roles WHERE rolname='dbo';")
        dboExist = cur.fetchall()[0][0]
        if dboExist == 0:
            cur.execute("Create role dbo with createdb createrole;")
        elif dboExist == 1:
            cur.execute("Alter role dbo with createdb createrole;")
        cur.execute("GRANT ALL PRIVILEGES ON DATABASE \"%s\" to dbo WITH GRANT OPTION;" % dbName)
        # Now create new user
        userName = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        cur.execute("SELECT COUNT(usename) from pg_catalog.pg_user where usename='%s';" % userName)
        userExist = cur.fetchall()[0][0]
        if userExist == 0:
            cur.execute("Create role \"{}\" with login password '{}';".format(userName, password))
        elif userExist == 1:
            cur.execute("Alter role \"{}\" with login password '{}';".format(userName, password))

        cur.execute("Grant dbo to \"{}\";".format(userName))
        cur.execute("Alter role \"{}\" set role dbo;".format(userName))
        cur.close()
        uri = "postgres://" + userName + ":" + password + "@" + host + ":" + str(port) + "/" + dbName
        credentials.update({'dbname': dbName, 'port': port, 'host': host, 'username': userName, 'password': password, 'uri': uri})
    except DatabaseError as error:
        if connection:
            connection.rollback()
        print("Errors happened while bind: %s" % error)
    finally:
        if connection:
            connection.close()
    return json.dumps(credentials)


def unbindService(host, port, accountName, accountPassword, dbName, userName):
    connectionString = "host={} port={} dbname={} user={} password={}".format(host, port, dbName, accountName, accountPassword)
    success = False
    credentials = {}
    try:
        connection = psycopg2.connect(connectionString)
        connection.autocommit = True
        cur = connection.cursor()
        cur.execute("SELECT COUNT(usename) from pg_catalog.pg_user where usename='%s';" % userName)
        userExist = cur.fetchall()[0][0]
        if userExist == 1:
            cur.execute("Drop owned by \"{}\";;".format(userName))
            cur.execute("Drop role \"{}\";".format(userName))
        cur.close()
        success = True
    except DatabaseError as error:
        if connection:
            connection.rollback()
        print("Error happened during unbind. Erros = %s" % error)
    finally:
        if connection:
            connection.close()
    return success


def changeMaintenanceWindowPeriod(client, dbInstanceId, time):
    request = ModifyDBInstanceMaintainTimeRequest.ModifyDBInstanceMaintainTimeRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_MaintainTime(time)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Setting Maintenance window failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def migrateZone(client, dbInstanceId, zone, switchId):
    request = MigrateToOtherZoneRequest.MigrateToOtherZoneRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_ZoneId(zone)
    request.set_VSwitchId(switchId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Migration of database instance failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def upgradeVersion(client, dbInstanceId, engineVersion):
    request = UpgradeDBInstanceEngineVersionRequest.UpgradeDBInstanceEngineVersionRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_EngineVersion(engineVersion)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Database engine upgrade failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None



####################################################################################################
################################## Backup and restore management functions #########################
####################################################################################################
def listBackUps(client, dbInstanceId, startTime, endTime):
    request = DescribeBackupsRequest.DescribeBackupsRequest()
    #Setting request parameters
    request.set_DBInstanceId(dbInstanceId)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while listing backups.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def backupDatabase(client, dbInstanceId):
    request = CreateBackupRequest.CreateBackupRequest()
    request.set_DBInstanceId(dbInstanceId)
    #request.set_BackupMethod("Logical")
    #request.set_BackupStrategy("instance")
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while backing-up DB instance.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def restoreDatabase(client, dbInstanceId, backupId):
    request = RestoreDBInstanceRequest.RestoreDBInstanceRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_BackupId(backupId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while restoring DB instance.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def cloneInstance(client, dbInstanceId, restoreTime):
    request = CloneDBInstanceRequest.CloneDBInstanceRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_RestoreTime(restoreTime)
    request.set_PayType("Postpaid")
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Database instance clone failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def createTemporaryInstance(client, dbInstanceId, backupId, restoreTime=None):
    request = CreateTempDBInstanceRequest.CreateTempDBInstanceRequest()
    request.set_DBInstanceId(dbInstanceId)
    # If you specify backupID the temporary instance will be created with data which is contained
    # in the backup respresented by the ID. Restoretime required for PITR.
    if restoreTime:
        request.set_RestoreTime(restoreTime)
    else:
        request.set_BackupId(backupId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Temporary instance creation failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def viewBackupPolicy(client, dbInstanceId, policyMode):
    request = DescribeBackupPolicyRequest.DescribeBackupPolicyRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_BackupPolicyMode(policyMode)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Request to view Backup policy failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def setBackupTime(client, dbInstanceId, backupTime):
    request = ModifyBackupPolicyRequest.ModifyBackupPolicyRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_BackupPolicyMode("DataBackupPolicy")
    request.set_PreferredBackupTime(backupTime)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Setting backup time failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def deleteBackup(client, dbInstanceId, backupId):
    request = DeleteBackupRequest.DeleteBackupRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_BackupId(backupId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Backup deletion failed.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None



####################################################################################################
####################################### Log Management Functions ###################################
####################################################################################################
def getErrorLogs(client, dbInstanceId, startTime, endTime):
    request = DescribeErrorLogsRequest.DescribeErrorLogsRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while listing error-logs!")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def getSlowLogDetails(client, dbInstanceId, startTime, endTime, dbName):
    request = DescribeSlowLogRecordsRequest.DescribeSlowLogRecordsRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    request.set_DBName(dbName)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while getting slow log details.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def querySQLAuditLogs(client, dbInstanceId, startTime, endTime, dbName):
    request = DescribeSQLLogRecordsRequest.DescribeSQLLogRecordsRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    request.set_Database(dbName)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while getting audit logs!")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def enableSqlCollectorPolicy(client, dbInstanceId):
    request = ModifySQLCollectorPolicyRequest.ModifySQLCollectorPolicyRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_SQLCollectorStatus("Enable")
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while enabling SQL collector policy.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


####################################################################################################
##################################### Monitoring related Functions #################################
####################################################################################################
def getResourceUsage(client, dbInstanceId):
    request = DescribeResourceUsageRequest.DescribeResourceUsageRequest()
    request.set_DBInstanceId(dbInstanceId)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while getting resource usage.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def setMonitoringPeriod(client, dbInstanceId, period):
    request = ModifyDBInstanceMonitorRequest.ModifyDBInstanceMonitorRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_Period(period)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while modifying monitoring period.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def getPerformanceUsage(client, dbInstanceId, startTime, endTime):
    request = DescribeDBInstancePerformanceRequest.DescribeDBInstancePerformanceRequest()
    request.set_DBInstanceId(dbInstanceId)
    request.set_Key("PGSQL_MemCpuUsage,PGSQL_SpaceUsage,PGSQL_IOPS,PSSQL_Sessions")
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while getting performance period.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


####################################################################################################
####################################### Miscellaneous Functions ####################################
####################################################################################################
def describeRegions(client):
    request = DescribeRegionsRequest.DescribeRegionsRequest()
    try:
        response = client.do_action_with_exception(request)
        return response
    except ServerException as exception:
        print("Error while describing regions.")
        print("HTTP statue = ", exception.get_http_status())
        print("HTTP Error code = ", exception.get_error_code())
        print("Error message = ", exception.get_error_msg())
    return None


def checkInstanceStatus(client, instanceId):
    # Creating request object
    request = DescribeDBInstanceAttributeRequest.DescribeDBInstanceAttributeRequest()
    # Setting request paramentes
    request.set_DBInstanceId(instanceId)
    response = client.do_action_with_exception(request)
    return json.loads(response.decode("utf-8"))['Items']['DBInstanceAttribute'][0]['DBInstanceStatus'].strip()


def instanceCreationTime(client, instanceId):
    startTime = time.time()
    while checkInstanceStatus(client, instanceId) != "Running":
        time.sleep(60)
    endTime = time.time()
    print("Time taken in instance creation = {} seconds".format(endTime - startTime))
    return
