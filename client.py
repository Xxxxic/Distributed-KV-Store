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
    def __init__(self):
        # 指向中间件服务器
        self.channel = grpc.insecure_channel('localhost:50003')
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


if __name__ == '__main__':
    client = KVClient()
    client.set_value("example_key", "example_value")  # 写入数据
    value = client.get_value("example_key")  # 从缓存读取数据
    print("Get Response:", value)

    client.del_value("example_key")  # 删除数据
    deleted_value = client.get_value("example_key")  # 尝试从缓存读取已删除的数据
    print("Get Response after delete:", deleted_value)