# AliCloud-PostgresRDS
This project uses AliBaba Cloud SDK to provide PostgreSQL database as a service. You can do operations like create-instance, delete-instance, backups etc., which are supported by Alibaba Cloud ApsaraDB for PostgreSQL RDS. Most of the functionality are written with perspective of using it in Cloud-foundry.

## Getting Started

These instructions will get you a copy of the project up and running on your machine for development and testing purposes.

### Prerequisites

You need python3.x to run the codes. You must have postgresql-client i.e. psql, installed on your machine.

### Installing

To install postgresql client on your machine run following command:

```
$ sudo apt-get install postgresql-client
```

You need to install AliBabaCloud SDK. Run following commands:

```
$ git clone https://github.com/aliyun/aliyun-openapi-python-sdk
$ cd aliyun-openapi-python-sdk
$ cd aliyun-python-sdk-core-v3
$ python3.x setup.py install
$ cd ../aliyun-python-sdk-ecs
$ python3.x setup.py install
$ cd ../aliyun-python-sdk-rds
$ python3.x setup.py install
```

While binding user it makes connections to postgresql, hence database driver would be required. Run folllowing command to install it.
```
$ pip3 install psycopg2-binary
```

## Running the tests

You can run all the functionalities using instance-manager.py. You can do following things by running instance-manager.py
* create-instance - Apsara db postgresql instance on Alicloud
* delete-instance
* create-initial-account
* create-database
* bind-service
* unbind-service

### Create Instance

To create an instance of PostgreSQL run following command

```
$ python3.x instance-manager.py accessKey.csv create-instance
```
Above command will create an instance in Germany region. If you want to change the region, open instance-manager.py file and change REGION_ID to desired value. When you run create-instance command and it gets executed successfully, it takes around 5-6 mins before the created instance comes in **Running** status. So, if you want to do some operation on the instance which you created then you must wait until instance status is Running. You can monitor the status of instance in Alibaba cloud console. If you want to create the instance in a VPC created by you in the same region, you should run following command:

```
$ python3.x instance-manager.py accessKey.csv create-instance <VPCId> <VSwitchId>
```
If instance gets created successfully, it will print a json object on stdout please save it for further use.

When you would have created the instance, the json object printed on stdout must have contained DBInstanceId. Use same DBInstanceID in the above command.

** We don't have control over the time taken by instance-creation, and hence we can not create the master account and database while instance creation itself. So, you must run following two commands in order to create master user account and the database. **

### Create initial/master account

When you run create-instance command and it gets executed successfully. It takes around 5-6 mins in order to be in Running status. So, if you want to do some operation on the instance which you created then you must wait for some time before you run some other commands. You can monitor the status of instance in Alibaba Console.

```
$ python3.x instance-manager.py accessKey.csv create-initial-account <DBInstanceId> <account name> <account password>
```
Above command will create a master account.

### Create database

To create database, run following command
```
$ python3.x instance-manager.py accessKey.csv create-database <host> <port> <master user> <master user password> <database name which you want to create>
```
host will be connectionString which got returnded in json object while instance-creation. Port was also returned in the same JSON object.

### Bind service

To bind a service, you should run following command
```
$ python3.x instance-manager.py accessKey.csv bind-service <host> <port> <master user> <master user password> <database name which you created>
```
The above command will return a json, which would be similar to VCAP.json which gets reflected in environment variable when we do cf bind-service.

### Unbind service

To unbind a service, you should run following command
```
$ python3.x instance-manager.py accessKey.csv unbind-service <host> <port> <master user> <master user password> <database name which you created> <username returned in json object while bind-service>
```
This command will basically delete the user which got created during bind-service. You must provide correct user name.

### Delete Instance

To delete an instance of Postgresql run following command

```
$ python3.x instance-manager.py accessKey.csv delete-instance <DBInstanceId>
```
## Authors

* **Akash Kumar**

See also the list of [contributors](https://github.com/akashkumar58/ali-apsara-pg-broker/graphs/contributors) who participated in this project.
