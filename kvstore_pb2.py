# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kvstore.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rkvstore.proto\"I\n\x07Request\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x11\n\toperation\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\x04\"+\n\x08Response\x12\x0e\n\x06result\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x04\"\xba\x01\n\x0f\x41llDataResponse\x12(\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x1a.AllDataResponse.DataEntry\x12\x0f\n\x07version\x18\x02 \x01(\x04\x1a\x43\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.AllDataResponse.Entry:\x02\x38\x01\x1a\'\n\x05\x45ntry\x12\r\n\x05value\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x04\x32k\n\x11MiddleWareService\x12%\n\x0cRouteRequest\x12\x08.Request\x1a\t.Response\"\x00\x12/\n\x0fRouteGetAllData\x12\x08.Request\x1a\x10.AllDataResponse\"\x00\x32\xb5\x01\n\tKVService\x12\x1c\n\x03Set\x12\x08.Request\x1a\t.Response\"\x00\x12\x1c\n\x03Get\x12\x08.Request\x1a\t.Response\"\x00\x12&\n\x06GetAll\x12\x08.Request\x1a\x10.AllDataResponse\"\x00\x12\x1f\n\x06\x44\x65lete\x12\x08.Request\x1a\t.Response\"\x00\x12#\n\nBackupData\x12\x08.Request\x1a\t.Response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'kvstore_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ALLDATARESPONSE_DATAENTRY']._options = None
  _globals['_ALLDATARESPONSE_DATAENTRY']._serialized_options = b'8\001'
  _globals['_REQUEST']._serialized_start=17
  _globals['_REQUEST']._serialized_end=90
  _globals['_RESPONSE']._serialized_start=92
  _globals['_RESPONSE']._serialized_end=135
  _globals['_ALLDATARESPONSE']._serialized_start=138
  _globals['_ALLDATARESPONSE']._serialized_end=324
  _globals['_ALLDATARESPONSE_DATAENTRY']._serialized_start=216
  _globals['_ALLDATARESPONSE_DATAENTRY']._serialized_end=283
  _globals['_ALLDATARESPONSE_ENTRY']._serialized_start=285
  _globals['_ALLDATARESPONSE_ENTRY']._serialized_end=324
  _globals['_MIDDLEWARESERVICE']._serialized_start=326
  _globals['_MIDDLEWARESERVICE']._serialized_end=433
  _globals['_KVSERVICE']._serialized_start=436
  _globals['_KVSERVICE']._serialized_end=617
# @@protoc_insertion_point(module_scope)