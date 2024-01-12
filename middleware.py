import random
import grpc
import kvstore_pb2
import kvstore_pb2_grpc
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
class MiddlewareServer(kvstore_pb2_grpc.MiddleWareServiceServicer):
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
            response = stub.GetAll(kvstore_pb2.Request(operation="GetAll"))

            # print(response.data)
            # 注意这里还不能直接转发MAP ，应该转换成对应的 Map：Entry 格式
            entries = {}
            for key, value in response.data.items():
                # print(f"{key}: {value}")
                # 添加 AllDataResponse.Entry 条目
                entries[key] = kvstore_pb2.AllDataResponse.Entry(value=value.value, version=value.version)

            return kvstore_pb2.AllDataResponse(data=entries)

        if request.operation == 'Set':
            response = stub.Set(
                kvstore_pb2.Request(key=request.key, value=request.value, operation="Set", version=request.version))
        elif request.operation == 'Get':
            response = stub.Get(kvstore_pb2.Request(key=request.key, operation="Get", version=request.version))
        elif request.operation == 'Delete':
            response = stub.Delete(kvstore_pb2.Request(key=request.key, operation="Delete", version=request.version))
        else:
            response = kvstore_pb2.Response(result="Invalid operation", version=request.version)
        # 返回响应时包含版本信息
        return kvstore_pb2.Response(result=response.result, version=response.version)

    def RouteLogin(self, request, context):
        responses = []
        for node in self.nodes:
            # print(f"Route Login request to {node}")
            channel = grpc.insecure_channel(node)
            stub = kvstore_pb2_grpc.KVServiceStub(channel)
            # 将登录信息发送到每个服务器，并收集它们的响应
            response = stub.Login(request)
            responses.append(response)

        # 出于简化考虑，只返回第一个响应，需要更详细的错误检查和处理
        return responses[0]

    # 获取所有数据
    # 获取所有数据
    def RouteGetAllData(self, request, context):
        if request.operation == 'GetAll':
            final_result = {}
            # 不同集群间的version就不考虑了
            # 因为数据分片，所以需要从所有节点获取数据
            for p in self.nodes:
                # 负载均衡：随机从主备节点中选择一个节点  [增加备份节点的权重]
                node_list = self.node_backup_map[p]

                primary_weight = 2  # 主节点权重
                backup_weight = 5  # 备份节点权重
                # 根据权重比例生成选择节点的列表
                nodes_to_choose = [p] * primary_weight + node_list * backup_weight

                # 若节点宕机，支持路由到其余节点
                get_flag = False
                # 重试机制(DONE)
                while len(nodes_to_choose) > 0:
                    # 随机选择节点
                    random_node = random.choice(nodes_to_choose)
                    try:
                        nodeSource = "Primary Node" if random_node == p else "Backup Node"
                        print(f"Route GetAll request to {random_node}   [{nodeSource}]")
                        channel = grpc.insecure_channel(f'{random_node}')
                        stub = kvstore_pb2_grpc.KVServiceStub(channel)
                        response = self._forward_request(stub, request)

                        for key, value in response.data.items():
                            # 添加 AllDataResponse.Entry 条目
                            final_result[key] = kvstore_pb2.AllDataResponse.Entry(value=value.value,
                                                                                  version=value.version)
                        get_flag = True
                        break
                    except grpc.RpcError as e:
                        print(f"Node {random_node} is down. Try to switch to other node...")
                        # 剔除无效节点：倒序遍历移除 否则会出错
                        for i in range(len(nodes_to_choose) - 1, -1, -1):
                            if nodes_to_choose[i] == random_node:
                                nodes_to_choose.pop(i)
                if get_flag:
                    continue
                else:
                    print("The master and backup cluster all down. Unable to process the request.")
                    print("=====================================")
                    return kvstore_pb2.AllDataResponse(
                        data={"Part of cluster are down": "Unable to process the request."})
            # 取得所有数据
            print("=====================================")
            # 返回节点响应
            return kvstore_pb2.AllDataResponse(data=final_result)
        else:
            print(f"Invalid operation: {request.operation}")
            print("=====================================")
            return kvstore_pb2.AllDataResponse(data={"Invalid operation": "Unable to process the request."})

    # 路由请求
    def RouteRequest(self, request, context):
        primary_node = self.hash.route(request.key)

        # 如果是Get请求，则支持路由到备份服务器，使得负载均衡
        # 宕机处理：如果节点宕机，则尝试路由到其他节点
        if request.operation == 'Get':
            # 负载均衡：随机从主备节点中选择一个节点  [增加备份节点的权重]
            node_list = self.node_backup_map[primary_node]

            # 设置主节点和备份节点的权重比例
            primary_weight = 2  # 主节点权重
            backup_weight = 5  # 备份节点权重
            # 根据权重比例生成选择节点的列表
            nodes_to_choose = [primary_node] * primary_weight + node_list * backup_weight

            # 若节点宕机，支持路由到其余节点
            # 重试机制(DONE)
            while len(nodes_to_choose) > 0:
                # 随机选择节点
                random_node = random.choice(nodes_to_choose)
                try:
                    nodeSource = "Primary Node" if random_node == primary_node else "Backup Node"
                    print(f"Route {request.operation} request to {random_node}   [{nodeSource}]")
                    channel = grpc.insecure_channel(f'{random_node}')
                    stub = kvstore_pb2_grpc.KVServiceStub(channel)
                    # 转发请求
                    response = self._forward_request(stub, request)
                    print("=====================================")
                    # 返回节点响应
                    return kvstore_pb2.Response(result=response.result, version=response.version)
                except grpc.RpcError as e:
                    print(f"Node {random_node} is down. Try to switch to other node...")
                    # 剔除无效节点：倒序遍历移除 否则会出错
                    for i in range(len(nodes_to_choose) - 1, -1, -1):
                        if nodes_to_choose[i] == random_node:
                            nodes_to_choose.pop(i)
            print("All nodes are down. Unable to process the request.")
            print("=====================================")
            return kvstore_pb2.Response(result="All nodes are down", version=request.version)
        # Set/Del请求：只能在主节点处理，如果节点宕机，则返回提示
        elif request.operation == 'Set' or request.operation == 'Delete':
            try:
                print(f"Route request to primary node {primary_node}")
                channel = grpc.insecure_channel(f'{primary_node}')
                stub = kvstore_pb2_grpc.KVServiceStub(channel)
                # 转发请求
                response = self._forward_request(stub, request)
                print("=====================================")
                # 返回主节点响应
                return kvstore_pb2.Response(result=response.result, version=response.version)
            except grpc.RpcError as e:
                print(f"Primary node {primary_node} is down. Unable to process the request.")
                print("=====================================")
                return kvstore_pb2.Response(result="Primary node is down. Unable to process the request.")
        else:
            print(f"Invalid operation: {request.operation}")
            # GetAll请求只能调用RouteGetAllData服务
            if request.operation == 'GetAll':
                print("Please call RouteGetAllData service to get all data.")
            print("=====================================")
            return kvstore_pb2.Response(result="Invalid operation", version=request.version)


# 启动中间件服务器
# 传入: 字典：{ 数据节点地址 : 备份节点list },  中间件服务器端口
def serverStart(nodes_, port_):
    print("=====================================")
    print("Starting Middleware Server ...")
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        kvstore_pb2_grpc.add_MiddleWareServiceServicer_to_server(MiddlewareServer(nodes_), server)
        server.add_insecure_port(f'localhost:{port_}')
        server.start()
        print(f"Middleware Server started at port {port_}")
        # 取出主从节点分别打印
        print()
        pNode = nodes_.keys()
        for p in pNode:
            print(f"Primary: {p}")
            for b in nodes_[p]:
                print(f"    Backup: {b}")
        print()
        print("Middleware Server Start Success!")
        print("=====================================")
        server.wait_for_termination()
    except Exception as e:
        print("Error: ", e)
        print("Middleware Server Start Failed!")
        print("=====================================")
        return False
