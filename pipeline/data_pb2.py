# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: data.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndata.proto\"(\n\x07Heatmap\x12\r\n\x05types\x18\x01 \x03(\x05\x12\x0e\n\x06values\x18\x02 \x03(\x02\"-\n\x08\x45nhancer\x12\x10\n\x08headings\x18\x01 \x03(\x05\x12\x0f\n\x07offsets\x18\x02 \x03(\x05\"\x95\x01\n\x08Metadata\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12+\n\tenhancers\x18\x02 \x03(\x0b\x32\x18.Metadata.EnhancersEntry\x12\x0f\n\x07\x66\x61\x63tors\x18\x03 \x03(\t\x1a;\n\x0e\x45nhancersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x18\n\x05value\x18\x02 \x01(\x0b\x32\t.Enhancer:\x02\x38\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _METADATA_ENHANCERSENTRY._options = None
  _METADATA_ENHANCERSENTRY._serialized_options = b'8\001'
  _HEATMAP._serialized_start=14
  _HEATMAP._serialized_end=54
  _ENHANCER._serialized_start=56
  _ENHANCER._serialized_end=101
  _METADATA._serialized_start=104
  _METADATA._serialized_end=253
  _METADATA_ENHANCERSENTRY._serialized_start=194
  _METADATA_ENHANCERSENTRY._serialized_end=253
# @@protoc_insertion_point(module_scope)
