# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: keyvalue.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ekeyvalue.proto\"I\n\x07Request\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x11\n\toperation\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\x04\"+\n\x08Response\x12\x0e\n\x06result\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x04\x32:\n\x11MiddleWareService\x12%\n\x0cRouteRequest\x12\x08.Request\x1a\t.Response\"\x00\x32h\n\tKVService\x12\x1c\n\x03Set\x12\x08.Request\x1a\t.Response\"\x00\x12\x1c\n\x03Get\x12\x08.Request\x1a\t.Response\"\x00\x12\x1f\n\x06\x44\x65lete\x12\x08.Request\x1a\t.Response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'keyvalue_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_REQUEST']._serialized_start=18
  _globals['_REQUEST']._serialized_end=91
  _globals['_RESPONSE']._serialized_start=93
  _globals['_RESPONSE']._serialized_end=136
  _globals['_MIDDLEWARESERVICE']._serialized_start=138
  _globals['_MIDDLEWARESERVICE']._serialized_end=196
  _globals['_KVSERVICE']._serialized_start=198
  _globals['_KVSERVICE']._serialized_end=302
# @@protoc_insertion_point(module_scope)
