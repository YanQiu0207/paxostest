from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AcceptReply(_message.Message):
    __slots__ = ["key", "maxbal", "maxval", "result"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    MAXBAL_FIELD_NUMBER: _ClassVar[int]
    MAXVAL_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    key: _any_pb2.Any
    maxbal: int
    maxval: _any_pb2.Any
    result: int
    def __init__(self, key: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., result: _Optional[int] = ..., maxbal: _Optional[int] = ..., maxval: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class AcceptRequest(_message.Message):
    __slots__ = ["bal", "key", "val"]
    BAL_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    bal: int
    key: _any_pb2.Any
    val: _any_pb2.Any
    def __init__(self, key: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., bal: _Optional[int] = ..., val: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class PrepareReply(_message.Message):
    __slots__ = ["key", "maxbal", "maxval", "result"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    MAXBAL_FIELD_NUMBER: _ClassVar[int]
    MAXVAL_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    key: _any_pb2.Any
    maxbal: int
    maxval: _any_pb2.Any
    result: int
    def __init__(self, key: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., result: _Optional[int] = ..., maxbal: _Optional[int] = ..., maxval: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class PrepareRequest(_message.Message):
    __slots__ = ["bal", "key"]
    BAL_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    bal: int
    key: _any_pb2.Any
    def __init__(self, key: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., bal: _Optional[int] = ...) -> None: ...

class ProposeReply(_message.Message):
    __slots__ = ["result"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class ProposeRequest(_message.Message):
    __slots__ = ["key", "val"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    key: _any_pb2.Any
    val: _any_pb2.Any
    def __init__(self, key: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., val: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
