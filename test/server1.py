import server
import asyncio

if __name__ == '__main__':
    server.serverStart(50001, ['localhost:50010'])
