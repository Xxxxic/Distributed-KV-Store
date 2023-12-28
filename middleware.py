import random
import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc
from concurrent import futures
import hashlib


# 一致性哈希
class ConsistentHash:
    def __init__(self, node_):
        self.nodes = node_

    def route(self, key):
        index = self.hash_function(key)
        return self.nodes[index]

    def hash_function(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % len(self.nodes)


# 中间件服务器
class MiddlewareServer(keyvalue_pb2_grpc.MiddleWareServiceServicer):
    def __init__(self, node_map_):
        # 备份节点信息
        self.node_backup_map = node_map_
        # 主节点
        self.nodes = list(node_map_.keys())
        # 哈希路由
        self.hash = ConsistentHash(self.nodes)

    # 消息转发
    def _forward_request(self, stub, request):
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

    # 路由请求
    def RouteRequest(self, request, context):
        primary_node = self.hash.route(request.key)

        # 如果是Get请求，则支持路由到备份服务器，使得负载均衡
        if request.operation == 'Get':
            backup_node_list = self.node_backup_map[primary_node]
            # 随机从备份节点中选择一个节点
            backup_node = backup_node_list[random.randint(0, len(backup_node_list) - 1)]
            print(f"Route request to primary node {backup_node}")
            try:
                channel = grpc.insecure_channel(f'{backup_node}')
                stub = keyvalue_pb2_grpc.KVServiceStub(channel)
                # 转发请求到备份节点
                response = self._forward_request(stub, request)
                # 返回备份节点响应
                return keyvalue_pb2.Response(result=response.result, version=response.version)
            except grpc.RpcError as e:
                print(f"Backup node {backup_node} is down. Unable to process the request.")

        # 其他操作类型的处理
        try:
            print(f"Route request to primary node {primary_node}")
            channel = grpc.insecure_channel(f'{primary_node}')
            stub = keyvalue_pb2_grpc.KVServiceStub(channel)
            # 转发请求
            response = self._forward_request(stub, request)
            # 返回主节点响应
            return keyvalue_pb2.Response(result=response.result, version=response.version)
        # 连接主节点失败
        except grpc.RpcError as e:
            print(f"Primary node {primary_node} is down. Try to switch to its backup node...")

            # 节点宕机，尝试路由到备份节点
            backup_node_list = self.node_backup_map[primary_node]
            # 遍历备份节点，找到对应的备份节点
            for backup_node in backup_node_list:
                print(f"Routing request to backup node {backup_node}")
                # 尝试连接备份节点
                try:
                    channel = grpc.insecure_channel(f'{backup_node}')
                    stub = keyvalue_pb2_grpc.KVServiceStub(channel)
                    # 转发请求到备份节点
                    response = self._forward_request(stub, request)
                    # 返回备份节点响应
                    return keyvalue_pb2.Response(result=response.result, version=response.version)
                except grpc.RpcError as e:
                    print(f"Backup node {backup_node} is also down. Unable to process the request.")
                    continue
            print("All nodes are down. Unable to process the request.")
            return keyvalue_pb2.Response(result="All nodes are down", version=request.version)


# 启动中间件服务器
# 传入: 字典：{ 数据节点地址 : 备份节点list },  中间件服务器端口
def serverStart(nodes_, port_):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_MiddleWareServiceServicer_to_server(MiddlewareServer(nodes_), server)
    server.add_insecure_port(f'localhost:{port_}')
    server.start()
    print(f"Middleware Server started at port {port_}")
    server.wait_for_termination()
