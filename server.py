import grpc
from concurrent import futures
import keyvalue_pb2
import keyvalue_pb2_grpc



class KVServicer(keyvalue_pb2_grpc.KVServiceServicer):
    def __init__(self):
        self.data = {}
        self.versions = {}  # 添加版本信息的存储

    def Set(self, request, context):
        current_version = self.versions.get(request.key, 0)
        print(f"Server Current version: {current_version}")
        # 版本不匹配，拒绝写入
        if request.version != current_version:
            print(f"Server Current version: {current_version}")
            return keyvalue_pb2.Response(result="Version mismatch, please try again", version = current_version)

        self.data[request.key] = request.value
        self.versions[request.key] = request.version + 1  # 更新版本号
        return keyvalue_pb2.Response(result="Set operation success", version=self.versions[request.key])

    def Get(self, request, context):
        value = self.data.get(request.key, "")
        return keyvalue_pb2.Response(result=value, version=self.versions.get(request.key, 0))

    def Delete(self, request, context):
        if request.key in self.data:
            del self.data[request.key]
            del self.versions[request.key]
            return keyvalue_pb2.Response(result="Delete operation success")
        else:
            return keyvalue_pb2.Response(result="Key not found for delete operation")


# 通过指定端口启动服务器
def serverStart(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_KVServiceServicer_to_server(KVServicer(), server)
    server.add_insecure_port(f'localhost:{port}')
    server.start()
    print(f"Server started at port {port}")
    server.wait_for_termination()
