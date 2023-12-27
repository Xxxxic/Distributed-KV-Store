import grpc
from concurrent import futures
import keyvalue_pb2
import keyvalue_pb2_grpc


# 简单的用户验证逻辑，实际中应使用更安全的方式
# def authenticate(username, password):
#     return (username == "user" and password == "password") or (username == "user1" and password == "password1") or (username == "user2" and password == "password2") or (username == "user3" and password == "password3")


class KVServicer(keyvalue_pb2_grpc.KVServiceServicer):
    def __init__(self):
        self.data = {}

    def Set(self, request, context):
        self.data[request.key] = request.value
        return keyvalue_pb2.Response(result="Set operation success")

    def Get(self, request, context):
        value = self.data.get(request.key, "")
        return keyvalue_pb2.Response(result=value)

    def Delete(self, request, context):
        if request.key in self.data:
            del self.data[request.key]
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
