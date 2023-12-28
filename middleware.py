import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc
from concurrent import futures
import hashlib


# 一致性哈希
class ConsistentHash:
    def __init__(self, nodes):
        self.nodes = nodes

    def hash_function(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % len(self.nodes)

    def route_request(self, key):
        index = self.hash_function(key)
        return self.nodes[index]


# 中间件服务器
class MiddlewareServer(keyvalue_pb2_grpc.MiddleWareServiceServicer):
    def __init__(self, middleware):
        self.middleware = middleware

    def RouteRequest(self, request, context):
        node = self.middleware.route_request(request.key)
        print(f"Route request to node {node}")
        channel = grpc.insecure_channel(f'{node}')
        stub = keyvalue_pb2_grpc.KVServiceStub(channel)

        # 将版本信息传递给数据节点
        if request.operation == 'Set':
            response = stub.Set(
                keyvalue_pb2.Request(key=request.key, value=request.value, operation="Set", version=request.version))
        elif request.operation == 'Get':
            response = stub.Get(keyvalue_pb2.Request(key=request.key, operation="Get", version=request.version))
        elif request.operation == 'Delete':
            response = stub.Delete(keyvalue_pb2.Request(key=request.key, operation="Delete", version=request.version))
        else:
            response = keyvalue_pb2.Response(result="Invalid operation", version=request.version)

        # 返回响应时包含版本信息
        return keyvalue_pb2.Response(result=response.result, version=response.version)


# 传入数据节点地址和中间件服务器端口，启动中间件服务器
def serverStart(nodes_, port_):
    nodes = nodes_  # 实际部署时的数据节点地址
    consistentHash = ConsistentHash(nodes)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_MiddleWareServiceServicer_to_server(MiddlewareServer(consistentHash), server)
    server.add_insecure_port(f'localhost:{port_}')
    server.start()
    print(f"Middleware Server started at port {port_}")
    server.wait_for_termination()
