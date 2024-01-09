import grpc
from concurrent import futures
from lib import kvstore_pb2
from lib import kvstore_pb2_grpc
import hashlib
import uuid    # 生成令牌

class KVServicer(kvstore_pb2_grpc.KVServiceServicer):
    def __init__(self, backup_server_address):
        self.data = {}
        self.versions = {}  # 添加版本信息的存储
        self.totalVersion = 0
        self.backup_server_address = backup_server_address
        # print("backup server: ", end='')
        # for i in backup_server_address:
        #     print(i + '  ')
        # 执行一次轮询，获取最新版本信息
        self.GetLatestVersionData()

        # 安全存储密码
        self.users = {
            "admin": hashlib.sha256("password".encode()).hexdigest(),
            "1": hashlib.sha256("1".encode()).hexdigest(),
            "2": hashlib.sha256("2".encode()).hexdigest(),
            "3": hashlib.sha256("3".encode()).hexdigest(),
        }  # 用户表
        self.tokens = {}  # 用户令牌

    def Login(self, request, context):
        # 下面是登录的处理过程
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        if request.user in self.users and self.users[request.user] == password_hash:
            token = str(uuid.uuid4())   # 生成唯一令牌
            self.tokens[request.user] = token
            print(f"Login success: {request.user} : {token}")
            return kvstore_pb2.LoginResponse(result="登录成功", token=token)
        else:
            print(f"Login failed: {request.user} : {request.password}")
            return kvstore_pb2.LoginResponse(result="用户名或密码错误")

    def check_token(self, user, token):
        return user in self.tokens and self.tokens[user] == token


    # 启动时轮询其他节点，获取最新版本信息
    def GetLatestVersionData(self):
        print("Try to get latest Data ...")
        # 连接到备份服务器，并执行轮询请求
        for address in self.backup_server_address:
            try:
                with grpc.insecure_channel(address) as channel:
                    stub = kvstore_pb2_grpc.KVServiceStub(channel)
                    response = stub.GetAll(kvstore_pb2.Request(operation="GetAll"))
                    # print(response.version)
                    # print(self.totalVersion)
                    if response.version > self.totalVersion:
                        print(f"Get latest version from backup server: {address}")
                        self.totalVersion = response.version
                        # 从response.data中提取值和版本信息
                        for key, value in response.data.items():
                            self.data[key] = value.value
                            self.versions[key] = value.version
            except:
                print(f"Backup server {address} is not available")
        print("Get latest data Done")

    # 连接到备份服务器，并执行数据同步请求
    def sync_to_backup(self, operation, key, value=None, version=None):
        # 遍历所有备份服务器
        for address in self.backup_server_address:
            with grpc.insecure_channel(address) as channel:
                stub = kvstore_pb2_grpc.KVServiceStub(channel)
                response = stub.BackupData(
                    kvstore_pb2.Request(operation=operation, key=key, value=value, version=version)
                )
                print(f'Backup to {address}, response: {response.result}')

    def Set(self, request, context):
        # if not self.check_token(request.user, request.token):
        #     return kvstore_pb2.Response(result="未登录或令牌无效")

        current_version = self.versions.get(request.key, 0)
        # print(f"Server Current version: {current_version}")
        # 版本不匹配，拒绝写入
        if request.version != current_version:
            # print(f"Server Current version: {current_version}")
            print("Set operation failed: Version mismatch, please try again")
            return kvstore_pb2.Response(result="Version mismatch, please try again", version=current_version)

        self.data[request.key] = request.value
        self.versions[request.key] = request.version + 1  # 更新版本号

        # 更新数据版本号
        self.totalVersion += 1

        # 向备份节点同步数据
        self.sync_to_backup("Set", request.key, request.value, self.versions[request.key])

        print("Set operation success")
        print("=====================================")
        return kvstore_pb2.Response(result="Set operation success", version=self.versions[request.key])

    def Get(self, request, context):
        # if not self.check_token(request.user, request.token):
        #     return kvstore_pb2.Response(result="未登录或令牌无效")

        value = self.data.get(request.key, "")
        print("Get operation success")
        print("=====================================")
        return kvstore_pb2.Response(result=value, version=self.versions.get(request.key, 0))

    def Delete(self, request, context):
        # if not self.check_token(request.user, request.token):
        #     return kvstore_pb2.Response(result="未登录或令牌无效")

        if request.key in self.data:
            # 将数据同步到备份服务器
            self.sync_to_backup(operation="Delete", key=request.key, version=self.versions[request.key])

            del self.data[request.key]
            del self.versions[request.key]
            # 更新数据版本号
            self.totalVersion += 1

            print("Delete operation success")
            print("=====================================")
            return kvstore_pb2.Response(result="Delete operation success")
        else:
            print("Delete operation failed: Key not found")
            print("=====================================")
            return kvstore_pb2.Response(result="Key not found for delete operation")

    def GetAll(self, request, context):
        # if not self.check_token(request.user, request.token):
        #     return kvstore_pb2.Response(result="未登录或令牌无效")

        # 注意这里不能直接转发，应该转换成对应的 Map：Entry 格式
        entries = {}
        for key, value in self.data.items():
            # print(f"{key}: {value}")
            # 添加 AllDataResponse.Entry 条目
            entries[key] = kvstore_pb2.AllDataResponse.Entry(value=value, version=self.versions[key])

        # print("get all data: ", end='')
        # print(entries)
        print("Get all data Success")
        print("=====================================")

        # 返回 AllDataResponse
        return kvstore_pb2.AllDataResponse(data=entries, version=self.totalVersion)


# 通过指定端口启动服务器
# 启动时传入启动端口、备份节点地址 注意是list
def serverStart(port, backup_add: list):
    print("=====================================")
    print("Server Start ...")
    print(f"Server start at port: {port}")
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        kvstore_pb2_grpc.add_KVServiceServicer_to_server(KVServicer(backup_add), server)
        server.add_insecure_port(f'localhost:{port}')
        server.start()
        print("Server Start Success!")
        print("=====================================")
        server.wait_for_termination()
    except Exception as e:
        print("Error: ", e)
        print("Server Start Failed!")
        print("=====================================")
