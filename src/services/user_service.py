from passmanager.user.v0.user_pb2_grpc import UserServicer


class UserService(UserServicer):

    def Register(self, request, context):
        return super().Register(request, context)

    def Username(self, request, context):
        return super().Username(request, context)

    def Delete(self, request, context):
        return super().Delete(request, context)

    def Health(self, request, context):
        return super().Health(request, context)
