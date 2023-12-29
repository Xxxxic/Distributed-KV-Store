import unittest


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here


import subprocess
import time
import threading


def start_server(port):
    subprocess.run(["python3", "server1.py", str(port), "backup_server_address_here"])


def start_middleware(port, backup_add):
    subprocess.run(["python3", "middle.py", str(port), "backup_server_address_here"])


def start_client():
    subprocess.run(["python3", "client1.py"])


if __name__ == "__main__":
    #    unittest.main()

    server_port = 50051
    backup_server_address = ["localhost:50002"]
    middleware_port = 50053

    # Start server and backup server threads
    server_thread = threading.Thread(target=start_server, args=(server_port,))
    server_thread.start()
    backup_server_thread = threading.Thread(target=start_server, args=(backup_server_address,))
    backup_server_thread.start()

    # Give some time for the servers to start
    time.sleep(2)

    # Start middleware server thread
    middleware_thread = threading.Thread(target=start_middleware, args=(middleware_port, backup_server_address,))
    middleware_thread.start()

    # Give some time for the middleware server to start
    time.sleep(2)

    # Start client
    start_client()