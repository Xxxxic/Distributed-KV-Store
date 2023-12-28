import time

import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc

from datetime import datetime, timedelta


# 用户数据缓存层
class Cache:
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.version = {}
        self.cache_ttl = timedelta(seconds=10)  # 设置缓存过期时间为 10 秒

    # 获取缓存中的版本信息
    def get_version_from_cache(self, key):
        if key in self.cache:
            return self.version[key]
        return None

    # 如果缓存中存在数据且未过期，则返回缓存中的数据
    def get_value_from_cache(self, key):
        if key in self.cache and datetime.now() < self.cache_expiry[key]:
            return self.cache[key]
        return None

    def set_cache(self, key, value, version, ttl):
        self.cache[key] = value
        self.version[key] = version
        # 设置缓存过期时间
        if ttl:
            self.cache_expiry[key] = datetime.now() + timedelta(seconds=ttl)
        else:
            self.cache_expiry[key] = datetime.now() + self.cache_ttl

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

    # Get
    # 先从本地缓存取，如果本地缓存存在且未过期，则直接返回；
    # 否则在服务器上检索这个键值对，并将新的不过期键值对 和 新版本信息 保存到缓存中。
    def get_value(self, key):
        cached_value = self.cache.get_value_from_cache(key)
        if cached_value:
            # print(f"Get from cache: {cached_value.result}")
            return cached_value, "cache"

        response = self.stub.RouteRequest(keyvalue_pb2.Request(key=key, operation="Get"))
        if response.result:
            self.cache.set_cache(key, response, response.version, ttl=20)
            # print(f"Get from server: {response.result}")
        return response.result, "server"

    # Set：直接发起set请求
    # 先检查缓存中的版本信息。
    # 如果版本匹配，说明这段时间没有人在修改值，直接在服务段更新值，将返回数据再写入缓存
    # 如果不匹配，那么会从服务器获取最新的版本信息和值，然后与服务器同步。
    def set_value(self, key, value, retries=3):
        # 重试机制
        while retries > 0:
            version = self.cache.get_version_from_cache(key) if self.cache.get_version_from_cache(key) else 0
            # print(f"Current version: {version}")
            response = self.stub.RouteRequest(
                keyvalue_pb2.Request(key=key, value=value, operation="Set", version=version))

            if response.result == "Invalid operation":
                print("Invalid operation")
                return response.result

            if response.result != "Version mismatch, please try again":
                # 版本匹配或者数据同步后，写入缓存
                self.cache.set_cache(key, value, response.version, ttl=10)
                return response.result  # 返回结果

            # 退让策略
            print("Version mismatch, try again after: ", 0.2 * retries)
            time.sleep(0.1 * retries)

            # 版本不匹配，重新获取最新的版本信息
            print("Get latest version from server: ", response.version)
            self.cache.set_cache(key, response.result, response.version, ttl=10)  # 重新设置缓存

        # 重试次数用完，返回错误信息
        return response.result

    # DELETE
    # 直接发起del请求，如果删除成功，则删除本地缓存
    # 如果delete操作的版本信息不匹配，那么系统会拒绝该操作。这确保了只有知道最新版本信息的客户端才能删除键值对，避免了并发删除带来的问题。成功删除后，本地缓存也会删除对应的键值对。
    def del_value(self, key):
        # 获取本地缓存的版本信息
        version = self.cache.get_version_from_cache(key) if self.cache.get_version_from_cache(key) else 0
        response = self.stub.RouteRequest(keyvalue_pb2.Request(key=key, operation="Delete", version=version))

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
            keys = command[1:]
            for key in keys:
                get_result = client.get_value(key)
                if (get_result[0] == ""):
                    print(f'{key} : Not exist     [ Get from {get_result[1]} ]')
                else:
                    print(f'{key} : {get_result[0]}     [ Get from {get_result[1]} ]')
        elif command[0] == "del":
            keys = command[1:]
            for key in keys:
                print(client.del_value(key))
        else:
            print("Invalid command.")
