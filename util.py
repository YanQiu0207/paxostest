
import google.protobuf.any_pb2 as any_pb2
import google.protobuf.wrappers_pb2 as wrappers_pb2

def PackMsgValue(oMessage, **kwargs):
    for key, val in kwargs.items():
        attr = getattr(oMessage, key, None)
        if not attr:
            continue
        if isinstance(val, int):
            int_value = wrappers_pb2.Int64Value(value=val)
            attr.Pack(int_value)
        elif isinstance(val, str):
            string_value = wrappers_pb2.StringValue(value=val)
            any_value = any_pb2.Any()
            any_value.Pack(string_value, "type.googleapis.com/google.protobuf.StringValue")
            attr.CopyFrom(any_value)
        else:
            continue
    return oMessage

def UnPackMsgValue(oMessage, key):
    attr = getattr(oMessage, key, None)
    if attr.Is(wrappers_pb2.Int64Value.DESCRIPTOR):
        int_value = wrappers_pb2.Int64Value()
        attr.Unpack(int_value)
        return int_value.value
    elif attr.Is(wrappers_pb2.StringValue.DESCRIPTOR):
        string_value = wrappers_pb2.StringValue()
        attr.Unpack(string_value)
        return string_value.value
    else:
        raise Exception("the attribute %s of %s is unsupported" % (key, oMessage))
