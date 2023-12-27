import grpc
import keyvalue_pb2
import keyvalue_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = keyvalue_pb2_grpc.KeyValueServiceStub(channel)

    # 使用合适的用户名和密码进行测试
    username = "user"
    password = "password"

    # Set 操作
    set_request = keyvalue_pb2.SetRequest(key="key1", value="value1", username=username, password=password)
    response = stub.Set(set_request)
    print("Set Response:", response)

    # Get 操作
    get_request = keyvalue_pb2.GetRequest(key="key1", username=username, password=password)
    response = stub.Get(get_request)
    print("Get Response:", response.value)

    # Delete 操作
    delete_request = keyvalue_pb2.DeleteRequest(key="key1", username=username, password=password)
    response = stub.Delete(delete_request)
    print("Delete Response:", response.success)

    # 再次尝试 Get 操作，检查是否成功删除
    response = stub.Get(get_request)
    print("Get Response after deletion:", response.value)


if __name__ == '__main__':
    run()
    # test_key_value_service()