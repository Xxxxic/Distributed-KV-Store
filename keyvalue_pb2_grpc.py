# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import keyvalue_pb2 as keyvalue__pb2


class MiddleWareServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RouteRequest = channel.unary_unary(
                '/MiddleWareService/RouteRequest',
                request_serializer=keyvalue__pb2.Request.SerializeToString,
                response_deserializer=keyvalue__pb2.Response.FromString,
                )


class MiddleWareServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RouteRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MiddleWareServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RouteRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RouteRequest,
                    request_deserializer=keyvalue__pb2.Request.FromString,
                    response_serializer=keyvalue__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'MiddleWareService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MiddleWareService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RouteRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/MiddleWareService/RouteRequest',
            keyvalue__pb2.Request.SerializeToString,
            keyvalue__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class KVServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Set = channel.unary_unary(
                '/KVService/Set',
                request_serializer=keyvalue__pb2.Request.SerializeToString,
                response_deserializer=keyvalue__pb2.Response.FromString,
                )
        self.Get = channel.unary_unary(
                '/KVService/Get',
                request_serializer=keyvalue__pb2.Request.SerializeToString,
                response_deserializer=keyvalue__pb2.Response.FromString,
                )
        self.Delete = channel.unary_unary(
                '/KVService/Delete',
                request_serializer=keyvalue__pb2.Request.SerializeToString,
                response_deserializer=keyvalue__pb2.Response.FromString,
                )
        self.BackupData = channel.unary_unary(
                '/KVService/BackupData',
                request_serializer=keyvalue__pb2.Request.SerializeToString,
                response_deserializer=keyvalue__pb2.Response.FromString,
                )


class KVServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Set(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BackupData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_KVServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Set': grpc.unary_unary_rpc_method_handler(
                    servicer.Set,
                    request_deserializer=keyvalue__pb2.Request.FromString,
                    response_serializer=keyvalue__pb2.Response.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=keyvalue__pb2.Request.FromString,
                    response_serializer=keyvalue__pb2.Response.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=keyvalue__pb2.Request.FromString,
                    response_serializer=keyvalue__pb2.Response.SerializeToString,
            ),
            'BackupData': grpc.unary_unary_rpc_method_handler(
                    servicer.BackupData,
                    request_deserializer=keyvalue__pb2.Request.FromString,
                    response_serializer=keyvalue__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'KVService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class KVService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Set(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/KVService/Set',
            keyvalue__pb2.Request.SerializeToString,
            keyvalue__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/KVService/Get',
            keyvalue__pb2.Request.SerializeToString,
            keyvalue__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/KVService/Delete',
            keyvalue__pb2.Request.SerializeToString,
            keyvalue__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BackupData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/KVService/BackupData',
            keyvalue__pb2.Request.SerializeToString,
            keyvalue__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
