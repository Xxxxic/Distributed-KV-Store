import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc

from datetime import datetime, timedelta


# 用户数据缓存层
class Cache:
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}

    def get_from_cache(self, key):
        if key in self.cache and datetime.now() < self.cache_expiry[key]:
            return self.cache[key]
        return None

    def set_cache(self, key, value, ttl=30):
        self.cache[key] = value
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=ttl)

    def delete_from_cache(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.cache_expiry[key]


class KVClient:
    def __init__(self, port_):
        # 指向中间件服务器
        self.channel = grpc.insecure_channel(f'localhost:{port_}')
        self.stub = keyvalue_pb2_grpc.MiddleWareServiceStub(self.channel)
        self.cache = Cache()

    def set_value(self, key, value):
        response = self.stub.RouteRequest(keyvalue_pb2.Request(key=key, value=value, operation="Set"))
        self.cache.set_cache(key, value)  # 更新本地缓存
        return response.result

    def get_value(self, key):
        cached_value = self.cache.get_from_cache(key)
        if cached_value:
            print(f"Get from cache: {cached_value} ")
            return cached_value

        response = self.stub.RouteRequest(keyvalue_pb2.Request(key=key, operation="Get"))
        if response.result:
            self.cache.set_cache(key, response.result)  # 缓存获取的值
            print(f"Get from server: {response.result} ")
        return response.result

    def del_value(self, key):
        response = self.stub.RouteRequest(keyvalue_pb2.Request(key=key, operation="Delete"))
        if response.result == "Delete operation success":
            self.cache.delete_from_cache(key)  # 仅当删除成功时才删除本地缓存
        return response.result


# 交互式客户端 需要传入中间件服务器地址
def ClientStart(port):
    client = KVClient(50003)
    help_text = """
        Commands Help:
        set key value —— Generate/Modify (key, value)
        get key —— Query (key, value) by the key
        del key —— Delete (key, value) by the key
        """

    while True:
        command = input("Enter command: ").split()  # 等待用户输入并将其拆分为列表
        if not command:
            continue
        if command[0] == "quit" or command[0] == "exit":  # 如果用户输入“退出”或“完毕”，则退出程序
            break
        if command[0] == "help":  # 如果用户输入"help"，打印命令帮助
            print(help_text)
            continue
        if len(command) < 2:
            print("Invalid command.")
            continue
        if command[0] == "set":
            if len(command) != 3:
                print("Invalid command. Usage: set key value")
                continue
            _, key, value = command
            print(client.set_value(key, value))
        elif command[0] == "get":
            _, key = command
            print(client.get_value(key))
        elif command[0] == "del":
            _, key = command
            print(client.del_value(key))
        else:
            print("Invalid command.")