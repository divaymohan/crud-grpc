import grpc
from concurrent import futures
import time
from sqlalchemy.orm import Session

import service_pb2
import service_pb2_grpc
from db.entity.user import User
from db.database import SessionLocal

# Implementing the gRPC service
class UserService(service_pb2_grpc.UserServiceServicer):
    
    def __init__(self):
        # Creating a session
        self.db_session = SessionLocal()

    def CreateUser(self, request, context):
        user = User(
            name=request.name,
            email=request.email,
            phone_number=request.phone_number,
            is_active=request.is_active
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return service_pb2.UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active
        )

    def GetUser(self, request, context):
        user = self.db_session.query(User).filter(User.id == request.id).first()
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, f"User with ID {request.id} not found")
        return service_pb2.UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active
        )

    def UpdateUser(self, request, context):
        user = self.db_session.query(User).filter(User.id == request.id).first()
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, f"User with ID {request.id} not found")
        
        user.name = request.name
        user.email = request.email
        user.phone_number = request.phone_number
        user.is_active = request.is_active
        self.db_session.commit()
        return service_pb2.UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active
        )

    def DeleteUser(self, request, context):
        user = self.db_session.query(User).filter(User.id == request.id).first()
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, f"User with ID {request.id} not found")
        
        self.db_session.delete(user)
        self.db_session.commit()
        return service_pb2.UserResponse(id=request.id, name="", email="", phone_number="", is_active=False)

    def ListUsers(self, request, context):
        users = self.db_session.query(User).all()
        user_responses = [service_pb2.UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active
        ) for user in users]
        return service_pb2.UserList(users=user_responses)


def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    start_grpc_server()
