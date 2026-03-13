from logging import getLogger
logger = getLogger("api")

from passmanager.data.v0.data_pb2_grpc import DataServicer
from passmanager.common.v0.error_pb2 import (
    HealthResponse
)

from data_handler import DataHandler


class DataService(DataServicer):

    def Create(self, request, context):
        logger.info("Create called by: %s", context.peer())
        return DataHandler.create(request)

    def Edit(self, request, context):
        logger.info("Edit called by: %s", context.peer())
        return DataHandler.edit(request)

    def Delete(self, request, context):
        logger.info("Delete called by: %s", context.peer())
        return DataHandler.delete(request)

    def Get(self, request, context):
        logger.info("Get called by: %s", context.peer())
        return DataHandler.get(request)

    def List(self, request, context):
        logger.info("List called by: %s", context.peer())
        return DataHandler.list(request)

    def Health(self, request, context):
        logger.info("Health called by: %s", context.peer())
        return HealthResponse(health=True)
