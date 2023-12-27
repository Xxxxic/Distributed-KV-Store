import client

if __name__ == '__main__':
    client = client.KVClient()

    client.set_value("example_key", "example_value")  # 写入数据
    value = client.get_value("example_key")  # 从缓存读取数据
    print("Get Response:", value)

    client.del_value("example_key")  # 删除数据
    deleted_value = client.get_value("example_key")  # 尝试从缓存读取已删除的数据
    print("Get Response after delete:", deleted_value)