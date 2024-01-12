from concurrent import futures
import grpc
import kvstore_pb2
import kvstore_pb2_grpc


class BackupServer(kvstore_pb2_grpc.KVServiceServicer):
    def __init__(self, primary_server_address_="localhost:50001"):
        self.backup_data = {}
        self.backup_versions = {}  # 添加版本信息的存储
        self.totalVersion = 0
        self.primary_server_address = primary_server_address_
        # 执行一次询问，获取最新版本信息
        self.GetLatestVersionData()

    def GetLatestVersionData(self):
        try:
            # 连接到主服务器，获取最新数据
            with grpc.insecure_channel(self.primary_server_address) as channel:
                stub = kvstore_pb2_grpc.KVServiceStub(channel)
                response = stub.GetAll(kvstore_pb2.Request(operation="GetAll"))
                # print(response.version)
                # print(self.totalVersion)
                if response.version > self.totalVersion:
                    print(f"Get latest version Data from primary server: {self.primary_server_address}")
                    self.totalVersion = response.version
                    # 从response.data中提取值和版本信息
                    for key, value in response.data.items():
                        self.backup_data[key] = value.value
                        self.backup_versions[key] = value.version
        except:
            print(f"Primary server {self.primary_server_address} is not available")
        print("Get latest data Done")

    # 接收来自主服务器的数据备份请求，并保存数据为备份数据
    # 如果是Set操作，则保存数据和版本信息
    # 如果是Delete操作，则删除数据和版本信息
    # 如果是Get操作，则返回 无效操作
    def BackupData(self, request, context):
        if request.operation == 'Set':
            self.backup_data[request.key] = request.value
            self.backup_versions[request.key] = request.version
            print(f'Backup Data    {request.key} : {request.value}')

            # 更新数据版本号
            self.totalVersion += 1
            # print("BackupServer Version: ", self.totalVersion)

            print(f"Backup Set success: {request.key} : {request.value}")
            print("=====================================")

            return kvstore_pb2.Response(result="Backup success")
        elif request.operation == 'Delete':
            if request.key in self.backup_data:
                del self.backup_data[request.key]
                del self.backup_versions[request.key]
                print("Backup Server Backup Data: Delete success")

                # 更新数据版本号
                self.totalVersion += 1
                # print("BackupServer Version: ", self.totalVersion)

                print("Backup Delete success: ", request.key)
                print("=====================================")

                return kvstore_pb2.Response(result="Backup success")
            else:
                print("Backup Data Failed: Key not found")
                print("=====================================")
                return kvstore_pb2.Response(result="Key not found in backup")
        else:
            print("Backup Data Failed: Invalid operation")
            print("=====================================")
            return kvstore_pb2.Response(result="Invalid operation")

    # 在备份服务器中提供Get服务
    def Get(self, request, context):
        if request.key in self.backup_data:
            value = self.backup_data[request.key]
            print(f"Get Value Sucess  {request.key} : {value}")
            print("=====================================")
            return kvstore_pb2.Response(result=self.backup_data[request.key],
                                         version=self.backup_versions.get(request.key, 0))
        else:
            print("Get Value: Key not found")
            print("=====================================")
            return kvstore_pb2.Response(result="Not exist")

    # 在备份服务器中提供GetAll服务
    def GetAll(self, request, context):
        # 注意这里不能直接转发，应该转换成对应的 Map：Entry 格式
        entries = {}
        for key, value in self.backup_data.items():
            print(f"{key}: {value}")
            # 添加 AllDataResponse.Entry 条目
            entries[key] = kvstore_pb2.AllDataResponse.Entry(value=value, version=self.backup_versions[key])

        print("Get all data Success")
        print("=====================================")

        # 返回 AllDataResponse
        return kvstore_pb2.AllDataResponse(data=entries, version=self.totalVersion)

    def Set(self, request, context):
        print("Backup Server: Invalid operation")
        print("=====================================")
        return kvstore_pb2.Response(result="Invalid operation")

    def Delete(self, request, context):
        print("Backup Server: Invalid operation")
        print("=====================================")
        return kvstore_pb2.Response(result="Invalid operation")


# 启动备份服务器
def backupServerStart(port, primary_server_address):
    print("=====================================")
    print("BackUp Server Start ...")
    print("Backup Server started at port " + str(port))
    print("Backup Of Primary Server: " + primary_server_address)
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        kvstore_pb2_grpc.add_KVServiceServicer_to_server(BackupServer(primary_server_address), server)
        server.add_insecure_port(f'localhost:{port}')
        server.start()
        print("BackUp Server Start Success!")
        print("=====================================")
        server.wait_for_termination()
    except Exception as e:
        print("Error: ", e)
        print("Backup Server Start Failed!")
        print("=====================================")
