import time
import grpc
from lib import kvstore_pb2
from lib import kvstore_pb2_grpc
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

    def set_cache(self, key, value, version, ttl=10):
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
        self.stub = kvstore_pb2_grpc.MiddleWareServiceStub(self.channel)
        self.cache = Cache()

        self.user = "admin"
        self.token = None

    def login(self):
        print("Please \033[94mLogin\033[0m First")
        while True:
            username = input("Input your username: ")
            password = input("Input your password: ")
            response = self.stub.RouteLogin(
                kvstore_pb2.LoginRequest(user=username, password=password)
            )
            if response.result == "登录成功":
                self.token = response.token
                print(f"\033[32mLogin success")
                print("\033[0m=======================================")
                break
            else:
                print(f"\033[35mLogin failed\033[0m: {response.result}, Please try again")

    # GetAll：直接发起getall请求
    def get_all(self):
        response = self.stub.RouteGetAllData(kvstore_pb2.Request(operation="GetAll"))
        # print(response)
        data_map = response.data  # 获取返回的 map 数据

        return data_map

    # Get
    # 先从本地缓存取，如果本地缓存存在且未过期，则直接返回；
    # 否则在服务器上检索这个键值对，并将新的不过期键值对 和 新版本信息 保存到缓存中。
    def get_value(self, key):
        cached_value = self.cache.get_value_from_cache(key)
        if cached_value:
            # print(f"Get from cache: {cached_value.result}")
            return cached_value, "cache"

        response = self.stub.RouteRequest(kvstore_pb2.Request(key=key, operation="Get"))
        if response.result:
            self.cache.set_cache(key, response.result, response.version)
            # print(f"Get from server: {response.result}")
        return response.result, "server"

    # Set：直接发起set请求
    # 先检查缓存中的版本信息。
    # 如果版本匹配，说明这段时间没有人在修改值，直接在服务段更新值，将返回数据再写入缓存
    # 如果不匹配，那么会从服务器获取最新的版本信息和值，然后与服务器同步。
    def set_value(self, key, value, retries=3):
        response = None
        # 重试机制
        while retries > 0:
            version = self.cache.get_version_from_cache(key) if self.cache.get_version_from_cache(key) else 0
            # print(f"Current version: {version}")
            response = self.stub.RouteRequest(
                kvstore_pb2.Request(key=key, value=value, operation="Set", version=version))

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
        if response:
            return response.result
        else:
            return "All nodes are down"

    # DELETE
    # 直接发起del请求，如果删除成功，则删除本地缓存
    # 如果delete操作的版本信息不匹配，那么系统会拒绝该操作。这确保了只有知道最新版本信息的客户端才能删除键值对，避免了并发删除带来的问题。成功删除后，本地缓存也会删除对应的键值对。
    def del_value(self, key):
        # 获取本地缓存的版本信息
        version = self.cache.get_version_from_cache(key) if self.cache.get_version_from_cache(key) else 0
        response = self.stub.RouteRequest(kvstore_pb2.Request(key=key, operation="Delete", version=version))

        if response.result == "Delete operation success":
            self.cache.delete_from_cache(key)  # 仅当删除成功时才删除本地缓存
        return response.result

    def terminalStart(self):
        help_text = """
    Commands Help:
    getall —— Get all (key, value) pairs
    get key —— Query (key, value) by the key
    set key value —— Generate/Modify (key, value)
    del key —— Delete (key, value) by the key
        """
        text = "\033[94mkvClient\033[0m "
        arrows = "\033[31m>\033[0m\033[32m>\033[0m\033[34m>\033[0m "

        while True:
            try:
                cmd = input(f"{text}{arrows}")

                command = cmd.split()  # 将命令拆分为列表
                if not command:
                    continue
                if command[0].lower() == "quit" or command[0].lower() == "exit":  # 如果用户输入“退出”或“完毕”，则退出程序
                    break
                if command[0].lower() == "help":  # 如果用户输入"help"，打印命令帮助
                    print(help_text)
                    continue

                if command[0].lower() == "getall":
                    result = self.get_all()
                    if len(result) == 0:
                        print("No data found")
                        continue
                    # 按照键值对的键排序
                    sorted_data = dict(sorted(result.items()))
                    # 遍历 map
                    for key, value in sorted_data.items():
                        print(f'{key} : {value.value}')
                    # print(result)
                elif command[0].lower() == "set":
                    if len(command) != 3:
                        print("Invalid command. Usage: set key value")
                        continue
                    _, key, value = command
                    print(self.set_value(key, value))
                elif command[0].lower() == "get":
                    keys = command[1:]
                    for key in keys:
                        get_result = self.get_value(key)
                        if get_result[0] == "All nodes are down":
                            print("All nodes are down! Please contact the administrator.")
                        elif get_result[0] == "":
                            print(f'{key} : Not exist     [ Get from {get_result[1]} ]')
                        else:
                            print(f'{key} : {get_result[0]}     [ Get from {get_result[1]} ]')
                elif command[0].lower() == "del":
                    keys = command[1:]
                    for key in keys:
                        print(self.del_value(key))
                else:
                    print("Invalid command. Please type 'help' to get help.")

            # except KeyboardInterrupt:  # Handling Ctrl+C to prevent abrupt exit
            #     print("\nUse 'quit' or 'exit' to exit the program.")
            #     continue
            except EOFError:  # Handling Ctrl+D to exit the program
                print("\nExiting program...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again or Restart the program.")


# 交互式客户端 需要传入中间件服务器地址
def ClientStart(port):
    print("=====================================")
    print("Client Start ...")
    client = KVClient(50003)
    print(f"Client start at port: {port}")
    print("Client Start Success!")
    print("=====================================")
    client.login()
    client.terminalStart()