import middleware

if __name__ == '__main__':
    middleware.serverStart(["localhost:50001", "localhost:50002"], 50003)