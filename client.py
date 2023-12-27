# import grpc
# import keyvalue_pb2
# import keyvalue_pb2_grpc
# import threading
#
#
# def set_get_delete_client(username, password):
#     channel = grpc.insecure_channel('localhost:50051')
#     stub = keyvalue_pb2_grpc.KeyValueServiceStub(channel)
#
#     # Set 操作
#     set_request = keyvalue_pb2.SetRequest(key=f"key-{username}", value=f"value-{username}", username=username, password=password)
#     response = stub.Set(set_request)
#     print(f"Set Response for {username}: {response}")
#
#     # Get 操作
#     get_request = keyvalue_pb2.GetRequest(key=f"key-{username}", username=username, password=password)
#     response = stub.Get(get_request)
#     print(f"Get Response for {username}: {response.value}")
#
#     # Delete 操作
#     delete_request = keyvalue_pb2.DeleteRequest(key=f"key-{username}", username=username, password=password)
#     response = stub.Delete(delete_request)
#     print(f"Delete Response for {username}: {response.success}")
#
#     # 再次尝试 Get 操作，检查是否成功删除
#     response = stub.Get(get_request)
#     print(f"Get Response after deletion for {username}: {response.value}")
#
# def run_multiple_clients():
#     # 模拟三个节点，分别用不同的用户名和密码
#     usernames = ["user1", "user2", "user3"]
#     passwords = ["password1", "password2", "password3"]
#
#     threads = []
#     for i in range(3):
#         thread = threading.Thread(target=set_get_delete_client, args=(usernames[i], passwords[i]))
#         threads.append(thread)
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#
# if __name__ == '__main__':
#     run_multiple_clients()


import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50053')
    stub = keyvalue_pb2_grpc.MiddleWareServiceStub(channel)

    request = keyvalue_pb2.Request(key="example_key", value="example_value", operation="Set")
    response = stub.RouteRequest(request)
    print("Set Response:", response)

    request = keyvalue_pb2.Request(key="example_key", operation="Get")
    response = stub.RouteRequest(request)
    print("Get Response:", response.result)

def run1():
    channel = grpc.insecure_channel('localhost:50003')
    stub = keyvalue_pb2_grpc.MiddleWareServiceStub(channel)

    request_set = keyvalue_pb2.Request(key="example_key", value="example_value", operation="Set")
    response_set = stub.RouteRequest(request_set)
    print("Set Response:", response_set.result)

    request_get = keyvalue_pb2.Request(key="example_key", operation="Get")
    response_get = stub.RouteRequest(request_get)
    print("Get Response:", response_get.result)

    request_delete = keyvalue_pb2.Request(key="example_key", operation="Delete")
    response_delete = stub.RouteRequest(request_delete)
    print("Delete Response:", response_delete.result)

if __name__ == '__main__':
    run1()
