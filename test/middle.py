import middleware

if __name__ == '__main__':
    # 单节点单备份测试
    # middleware.serverStart({"localhost:50001": ['localhost:50010']}, 50003)

    # 多节点多备份测试
    middleware.serverStart({"localhost:50001":['localhost:50011'], "localhost:50002":['localhost:50012']}, 50003)
