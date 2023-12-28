from concurrent import futures
import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc


class BackupServer(keyvalue_pb2_grpc.KVServiceServicer):
    def __init__(self):
        self.backup_data = {}
        self.backup_versions = {}  # 添加版本信息的存储

    # 接收来自主服务器的数据备份请求，并保存数据为备份数据
    # 如果是Set操作，则保存数据和版本信息
    # 如果是Delete操作，则删除数据和版本信息
    # 如果是Get操作，则返回 无效操作
    def BackupData(self, request, context):
        print(request)
        if request.operation == 'Set':
            self.backup_data[request.key] = request.value
            self.backup_versions[request.key] = request.version
            print(f'Backup Server Backup Data: {request.key} - {request.value}')
            return keyvalue_pb2.Response(result="Backup success")
        elif request.operation == 'Delete':
            if request.key in self.backup_data:
                del self.backup_data[request.key]
                del self.backup_versions[request.key]
                print("Backup Server Backup Data: Delete success")
                return keyvalue_pb2.Response(result="Backup success")
            else:
                print("Backup Server Backup Data: Key not found")
                return keyvalue_pb2.Response(result="Key not found in backup")
        else:
            print("Backup Server Backup Data: Invalid operation")
            return keyvalue_pb2.Response(result="Invalid operation")

    # 在备份服务器中提供Get服务
    def Get(self, request, context):
        if request.key in self.backup_data:
            value = self.backup_data[request.key]
            print("Backup Server Get Value: " + value)
            return keyvalue_pb2.Response(result=self.backup_data[request.key],
                                         version=self.backup_versions.get(request.key, 0))
        else:
            print("Backup Server Get Value: Key not found")
            return keyvalue_pb2.Response(result="Key not found in backup")

    def Set(self, request, context):
        print("Backup Server: Invalid operation")
        return keyvalue_pb2.Response(result="Invalid operation")

    def Delete(self, request, context):
        print("Backup Server: Invalid operation")
        return keyvalue_pb2.Response(result="Invalid operation")


# 启动备份服务器
def backupServerStart(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_KVServiceServicer_to_server(BackupServer(), server)
    server.add_insecure_port(f'localhost:{port}')
    server.start()
    print("Backup Server started at port " + str(port))
    server.wait_for_termination()
