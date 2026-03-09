import grpc
from concurrent import futures

from logging import getLogger
logger = getLogger("api")

import passmanager.user.v0.user_pb2_grpc as user_grpc
import passmanager.password.v0.password_pb2_grpc as password_grpc
import passmanager.session.v0.session_pb2_grpc as session_grpc
import passmanager.data.v0.data_pb2_grpc as data_grpc

from user_service import UserService
from password_service import PasswordService
from session_service import SessionService
from data_service import DataService


def serve():

    # TODO - Use real server credentials
    server_credentials = grpc.local_server_credentials()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    user_grpc.add_UserServicer_to_server(
        UserService(),
        server
    )

    password_grpc.add_PasswordServicer_to_server(
        PasswordService(),
        server
    )

    session_grpc.add_SessionServicer_to_server(
        SessionService(),
        server
    )

    data_grpc.add_DataServicer_to_server(
        DataService(),
        server
    )

    # TODO - Define specific port
    server.add_secure_port("[::]:50051", server_credentials)
    server.start()

    logger.info("Server running on port 50051")
    server.wait_for_termination()
