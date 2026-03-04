from passmanager.data.v0.data_pb2_grpc import DataServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from data_handler import DataHandler


class DataService(DataServicer):

    def Create(self, request, context):
        return DataHandler.create(request)

    def Edit(self, request, context):
        return DataHandler.edit(request)

    def Delete(self, request, context):
        return DataHandler.delete(request)

    def Get(self, request, context):
        return DataHandler.get(request)

    def List(self, request, context):
        return DataHandler.list(request)

    def Health(self, request, context):
        return HealthResponse(health=True)
