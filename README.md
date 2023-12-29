## =_=


> **generate proto files with:**
> 
> `python -m grpc_tools.protoc -I=./lib --python_out=. --grpc_python_out=./lib kvstore.proto
` 
> 
> generate `kvstore_pb2_grpc.py`(./lib) and `kvstore_pb2.py`
>

##  🫠TODO
1. Asynchronous Backup (Or multi-threading)
2. ~~Raft/Paxos~~
3. User security 
4. User isolation
5. Consistent hash: additions and deletions of nodes
