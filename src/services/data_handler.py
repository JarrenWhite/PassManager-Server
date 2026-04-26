from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.data.v0.data_payloads_pb2 import (
    DataCreateRequest,
    DataCreateResponse,
    DataEditRequest,
    DataEditResponse,
    DataDeleteRequest,
    DataDeleteResponse,
    DataGetRequest,
    DataGetResponse,
    DataListRequest,
    DataListResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure
)

from utils import ServiceUtils, SessionManager, DBUtilsData
from enums import FailureReason


class DataHandler:

    @staticmethod
    def create(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = DataCreateRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_entry_name(request.entry_name)
        if status:
            error_list.append(status.error_proto("entry_name"))
        status = ServiceUtils.sanitise_entry_data(request.entry_data)
        if status:
            error_list.append(status.error_proto("entry_data"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason, public_id = DBUtilsData.create(
            user_id=user_id,
            entry_name=request.entry_name,
            entry_data=request.entry_data
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        response = DataCreateResponse(
            username_hash=request.username_hash,
            entry_public_id=public_id
        )
        return SessionManager.seal_session(
            session_id=secure_request.session_id,
            response=response.SerializeToString()
        )


    @staticmethod
    def edit(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = DataEditRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_entry_public_id(request.entry_public_id)
        if status:
            error_list.append(status.error_proto("entry_public_id"))
        if request.HasField("entry_name"):
            status = ServiceUtils.sanitise_entry_name(request.entry_name)
            if status:
                error_list.append(status.error_proto("entry_name"))
        if request.HasField("entry_data"):
            status = ServiceUtils.sanitise_entry_data(request.entry_data)
            if status:
                error_list.append(status.error_proto("entry_data"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason = DBUtilsData.edit(
            user_id=user_id,
            public_id=request.entry_public_id,
            entry_name=request.entry_name if request.HasField("entry_name") else None,
            entry_data=request.entry_data if request.HasField("entry_data") else None
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        response = DataEditResponse(
            username_hash=request.username_hash,
            entry_public_id=request.entry_public_id
        )
        return SessionManager.seal_session(
            session_id=secure_request.session_id,
            response=response.SerializeToString()
        )


    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = DataDeleteRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_entry_public_id(request.entry_public_id)
        if status:
            error_list.append(status.error_proto("entry_public_id"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason = DBUtilsData.delete(
            user_id=user_id,
            public_id=request.entry_public_id
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        response = DataDeleteResponse(
            username_hash=request.username_hash,
            entry_public_id=request.entry_public_id
        )
        return SessionManager.seal_session(
            session_id=secure_request.session_id,
            response=response.SerializeToString()
        )


    @staticmethod
    def get(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = DataGetRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))
        status = ServiceUtils.sanitise_entry_public_id(request.entry_public_id)
        if status:
            error_list.append(status.error_proto("entry_public_id"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason, entry_name, entry_data = DBUtilsData.get_entry(
            user_id=user_id,
            public_id=request.entry_public_id
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        response = DataGetResponse(
            username_hash=request.username_hash,
            entry_public_id=request.entry_public_id,
            entry_name=entry_name,
            entry_data=entry_data
        )
        return SessionManager.seal_session(
            session_id=secure_request.session_id,
            response=response.SerializeToString()
        )


    @staticmethod
    def list(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Convert to Protobuf Message
        try:
            request = DataListRequest.FromString(decrypted_bytes)
        except DecodeError:
            error_list.append(FailureReason.DECRYPTION.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Sanitise Inputs
        status = ServiceUtils.sanitise_username(request.username_hash)
        if status:
            error_list.append(status.error_proto("username_hash"))

        # Return Errors
        if len(error_list) > 0:
            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Call Util function
        status, failure_reason, entry_list = DBUtilsData.get_list(
            user_id=user_id
        )

        # Return error
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        # Successful Return
        response = DataListResponse(
            username_hash=request.username_hash,
            entry_details=[
                DataListResponse.EntryDetails(
                    entry_public_id=entry_public_id,
                    entry_name=entry_name
                )
                for entry_public_id, entry_name in entry_list.items()
            ]
        )
        return SessionManager.seal_session(
            session_id=secure_request.session_id,
            response=response.SerializeToString()
        )
