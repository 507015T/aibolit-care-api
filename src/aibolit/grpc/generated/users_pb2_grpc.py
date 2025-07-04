# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from aibolit.grpc.generated import users_pb2 as aibolit_dot_grpc_dot_generated_dot_users__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in aibolit/grpc/generated/users_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class UserServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateUser = channel.unary_unary(
                '/user.UserService/CreateUser',
                request_serializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserRequest.SerializeToString,
                response_deserializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserResponse.FromString,
                _registered_method=True)
        self.GetUsers = channel.unary_unary(
                '/user.UserService/GetUsers',
                request_serializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersRequest.SerializeToString,
                response_deserializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersResponse.FromString,
                _registered_method=True)


class UserServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUsers(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateUser': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateUser,
                    request_deserializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserRequest.FromString,
                    response_serializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserResponse.SerializeToString,
            ),
            'GetUsers': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUsers,
                    request_deserializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersRequest.FromString,
                    response_serializer=aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'user.UserService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('user.UserService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class UserService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/user.UserService/CreateUser',
            aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserRequest.SerializeToString,
            aibolit_dot_grpc_dot_generated_dot_users__pb2.CreateUserResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetUsers(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/user.UserService/GetUsers',
            aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersRequest.SerializeToString,
            aibolit_dot_grpc_dot_generated_dot_users__pb2.GetAllUsersResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
