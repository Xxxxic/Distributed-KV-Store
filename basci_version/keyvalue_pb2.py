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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ekeyvalue.proto\"L\n\nSetRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x10\n\x08password\x18\x04 \x01(\t\"\x1e\n\x0bSetResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"=\n\nGetRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"\x1c\n\x0bGetResponse\x12\r\n\x05value\x18\x01 \x01(\t\"@\n\rDeleteRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\"!\n\x0e\x44\x65leteResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\x86\x01\n\x0fKeyValueService\x12\"\n\x03Set\x12\x0b.SetRequest\x1a\x0c.SetResponse\"\x00\x12\"\n\x03Get\x12\x0b.GetRequest\x1a\x0c.GetResponse\"\x00\x12+\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\x0f.DeleteResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'keyvalue_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_SETREQUEST']._serialized_start=18
  _globals['_SETREQUEST']._serialized_end=94
  _globals['_SETRESPONSE']._serialized_start=96
  _globals['_SETRESPONSE']._serialized_end=126
  _globals['_GETREQUEST']._serialized_start=128
  _globals['_GETREQUEST']._serialized_end=189
  _globals['_GETRESPONSE']._serialized_start=191
  _globals['_GETRESPONSE']._serialized_end=219
  _globals['_DELETEREQUEST']._serialized_start=221
  _globals['_DELETEREQUEST']._serialized_end=285
  _globals['_DELETERESPONSE']._serialized_start=287
  _globals['_DELETERESPONSE']._serialized_end=320
  _globals['_KEYVALUESERVICE']._serialized_start=323
  _globals['_KEYVALUESERVICE']._serialized_end=457
# @@protoc_insertion_point(module_scope)
