import unittest


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here

import subprocess
import time


if __name__ == "__main__":
    server_port = 50051
    backup_server_address = ["localhost:50002"]
    middleware_port = 50053

    # Start server, middleware, and client in different terminals
    subprocess.Popen(["osascript", "-e", "python3", "server1.py", str(server_port), "server_address_here"])
    subprocess.Popen(["osascript", "-e", "python3", "backup1.py", str(backup_server_address), "backup_server_address_here"])
    time.sleep(2)  # Add a delay before starting middleware and client
    subprocess.Popen(["osascript", "-e", "python3", "middle.py", str(middleware_port), "backup_server_address_here"])
    time.sleep(2)
    subprocess.Popen(["osascript", "-e", "python3", "client1.py"])

    