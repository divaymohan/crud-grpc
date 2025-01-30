import grpc
import service_pb2
import service_pb2_grpc

# Establish gRPC connection
channel = grpc.insecure_channel('localhost:50051')
stub = service_pb2_grpc.UserServiceStub(channel)

def create_user(name, email, phone_number, is_active):
    request = service_pb2.UserRequest(
        name=name,
        email=email,
        phone_number=phone_number,
        is_active=is_active
    )
    response = stub.CreateUser(request)
    print(f"User Created: {response}")

def get_user(user_id):
    request = service_pb2.UserRequest(id=user_id)
    try:
        response = stub.GetUser(request)
        print(f"User Found: {response}")
    except grpc.RpcError as e:
        print(f"Error: {e.code()} - {e.details()}")

def update_user(user_id, name, email, phone_number, is_active):
    request = service_pb2.UserRequest(
        id=user_id,
        name=name,
        email=email,
        phone_number=phone_number,
        is_active=is_active
    )
    try:
        response = stub.UpdateUser(request)
        print(f"User Updated: {response}")
    except grpc.RpcError as e:
        print(f"Error: {e.code()} - {e.details()}")

def delete_user(user_id):
    request = service_pb2.UserRequest(id=user_id)
    try:
        response = stub.DeleteUser(request)
        print(f"User Deleted: ID {response.id}")
    except grpc.RpcError as e:
        print(f"Error: {e.code()} - {e.details()}")

def list_users():
    request = service_pb2.Empty()
    response = stub.ListUsers(request)
    print("Users List:")
    for user in response.users:
        print(user)

if __name__ == '__main__':
    # Test all CRUD operations
    print("\n### Creating Users ###")
    create_user("Mohan", "mohan@gmail.com", "8149958194", True)
    create_user("Geetansh", "geetansh@gmail.com", "9934567890", True)

    print("\n### Listing Users ###")
    list_users()

    print("\n### Fetching a User ###")
    get_user(1)  # Assuming ID 1 exists

    print("\n### Updating a User ###")
    update_user(1, "Divay Updated", "divay.updated@gmail.com", "9999999999", False)

    print("\n### Fetching Updated User ###")
    get_user(1)

    print("\n### Deleting a User ###")
    delete_user(2)  # Assuming ID 2 exists

    print("\n### Final Users List ###")
    list_users()
