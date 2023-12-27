import grpc
from concurrent import futures
import keyvalue_pb2
import keyvalue_pb2_grpc

# 简单的用户验证逻辑，实际中应使用更安全的方式
def authenticate(username, password):
    return username == "user" and password == "password"


class KeyValueServicer(keyvalue_pb2_grpc.KeyValueServiceServicer):
    def __init__(self):
        self.data = {}

    def Set(self, request, context):
        if authenticate(request.username, request.password):
            self.data[request.key] = request.value
            return keyvalue_pb2.SetResponse(success=True)
        else:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return keyvalue_pb2.SetResponse(success=False)

    def Get(self, request, context):
        if authenticate(request.username, request.password):
            value = self.data.get(request.key, "")
            return keyvalue_pb2.GetResponse(value=value)
        else:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return keyvalue_pb2.GetResponse(value="")

    def Delete(self, request, context):
        if authenticate(request.username, request.password):
            if request.key in self.data:
                del self.data[request.key]
                return keyvalue_pb2.DeleteResponse(success=True)
            else:
                return keyvalue_pb2.DeleteResponse(success=False)
        else:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return keyvalue_pb2.DeleteResponse(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_KeyValueServiceServicer_to_server(KeyValueServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()