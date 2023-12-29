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
        if request.operation == 'GetAll':
            response = stub.GetAll(keyvalue_pb2.Request(operation="GetAll"))

            # print(response.data)
            # 注意这里还不能直接转发MAP ，应该转换成对应的 Map：Entry 格式
            entries = {}
            for key, value in response.data.items():
                # print(f"{key}: {value}")
                # 添加 AllDataResponse.Entry 条目
                entries[key] = keyvalue_pb2.AllDataResponse.Entry(value=value.value, version=value.version)

            return keyvalue_pb2.AllDataResponse(data=entries)

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

    # 获取所有数据
    def RouteGetAllData(self, request, context):
        if request.operation == 'GetAll':
            # 随机从主节点和备份节点中选择一个节点
            primary_node = self.hash.route(request.key)
            backup_node_list = self.node_backup_map[primary_node]
            backup_node_list.append(primary_node)
            random_node = backup_node_list[random.randint(0, len(backup_node_list) - 1)]
            source = "Primary Node" if random_node == primary_node else "Backup Node"
            print(f"Route request to node: {random_node}   [{source}]")

            try:
                channel = grpc.insecure_channel(f'{random_node}')
                stub = keyvalue_pb2_grpc.KVServiceStub(channel)
                response = self._forward_request(stub, request)
                return keyvalue_pb2.AllDataResponse(data=response.data)
            except grpc.RpcError as e:
                print(f"Node {random_node} is down. Unable to process the request!")
                # TODO: 重试机制
        else:
            print(f"Invalid operation: {request.operation}")
            return keyvalue_pb2.AllDataResponse(data={})

    # 路由请求
    def RouteRequest(self, request, context):
        primary_node = self.hash.route(request.key)

        # 如果是Get请求，则支持路由到备份服务器，使得负载均衡
        # 宕机处理：如果节点宕机，则尝试路由到其他节点
        if request.operation == 'Get':
            # 随机从主备节点中选择一个节点
            primary_node = self.hash.route(request.key)
            node_list = self.node_backup_map[primary_node]
            node_list.append(primary_node)
            # print(node_list)
            random_idx = [i for i in range(len(node_list))]
            # 若节点宕机，支持路由到其余节点
            # 重试机制(DONE)
            while len(random_idx) > 0:
                idx = random_idx.pop(random.randint(0, len(random_idx) - 1))
                # print(idx, len(random_idx), len(node_list))
                random_node = node_list[idx]
                try:
                    nodeSource = "Primary Node" if random_node == primary_node else "Backup Node"
                    print(f"Route request to node: {random_node}   [{nodeSource}]")
                    channel = grpc.insecure_channel(f'{random_node}')
                    stub = keyvalue_pb2_grpc.KVServiceStub(channel)
                    # 转发请求
                    response = self._forward_request(stub, request)
                    # 返回节点响应
                    return keyvalue_pb2.Response(result=response.result, version=response.version)
                except grpc.RpcError as e:
                    print(f"Node {random_node} is down. Try to switch to other node...")
            print("All nodes are down. Unable to process the request.")
            return keyvalue_pb2.Response(result="All nodes are down", version=request.version)
        # Set/Del请求：只能在主节点处理，如果节点宕机，则返回提示
        elif request.operation == 'Set' or request.operation == 'Delete':
            try:
                print(f"Route request to primary node {primary_node}")
                channel = grpc.insecure_channel(f'{primary_node}')
                stub = keyvalue_pb2_grpc.KVServiceStub(channel)
                # 转发请求
                response = self._forward_request(stub, request)
                # 返回主节点响应
                return keyvalue_pb2.Response(result=response.result, version=response.version)
            except grpc.RpcError as e:
                print(f"Primary node {primary_node} is down. Unable to process the request.")
                return keyvalue_pb2.Response(result="Primary node is down. Unable to process the request.")
        else:
            print(f"Invalid operation: {request.operation}")
            # GetAll请求只能调用RouteGetAllData服务
            if request.operation == 'GetAll':
                print("Please call RouteGetAllData service to get all data.")
            return keyvalue_pb2.Response(result="Invalid operation", version=request.version)



# 启动中间件服务器
# 传入: 字典：{ 数据节点地址 : 备份节点list },  中间件服务器端口
def serverStart(nodes_, port_):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvalue_pb2_grpc.add_MiddleWareServiceServicer_to_server(MiddlewareServer(nodes_), server)
    server.add_insecure_port(f'localhost:{port_}')
    server.start()
    print(f"Middleware Server started at port {port_}")
    server.wait_for_termination()