# gRPC (Google Remote Procedure Calls)

In this article you will learn basics of gRPC. How we can build CRUD apis using gRPC. Before doing that let's have a glimbs about what gRPC is in actual. 

**What is gRPC?**

gRPC (gRPC Remote Procedure Call) is a high-performance, open-source framework developed by Google that enables communication between distributed systems. It is designed for efficiency, scalability, and cross-platform support.

gRPC uses Protobuf as its interface definition language (IDL) for defining service methods and message formats, making data exchange efficient and compact.

![gRPC](grpc.png)

**When to Use gRPC?**

* Microservices communication with low latency.
* High-performance APIs that need efficient data serialization.
* Real-time streaming applications (e.g., chat apps, video streaming).
* Cloud-native applications requiring language interoperability.

### Implementation

#### Database layer 

Let's create a  `database.py` file which will responsible for creating database session. You can choose any database and modify it accordingly. Here i am using mysql for simplicity.

```py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/proto_demo"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

```

Now, Creating a very simple user entity with basic information of a user (`user.py`).

```py
from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean)

```

It is enough as of now. In gRPC, a client application can directly call a method on a server application on a different machine. As in many RPC systems, gRPC is based around the idea of defining a service, specifying the methods that can be called remotely with their parameters and return types. On the server side, the server implements this interface and runs a gRPC server to handle client calls. On the client side, the client has a stub (referred to as just a client in some languages) that provides the same methods as the server.

gRPC clients and servers can run and talk to each other in a variety of environments - from servers inside Google to your own desktop - and can be written in any of gRPC’s supported languages. So, for example, you can easily create a gRPC server in Java with clients in Go, Python, or Ruby. In addition, the latest Google APIs will have gRPC versions of their interfaces, letting you easily build Google functionality into your applications.

### Working with protobuf

By default, gRPC uses Protocol Buffers, Google’s mature open source mechanism for serializing structured data (although it can be used with other data formats such as JSON). Here’s a quick intro to how it works.

Protocol buffer data is structured as messages, where each message is a small logical record of information containing a series of name-value pairs called fields.

#### Step 1

The first step when working with protocol buffers is to define the structure for the data you want to serialize in a proto file: this is an ordinary text file with a .proto extension.

In our case its user data. 
```proto

message UserRequest {
  int32 id = 1;
  string name = 2;
  string email = 3;
  string phone_number = 4;
  bool is_active = 5;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  string phone_number = 4;
  bool is_active = 5;
}

message UserList {
    repeated UserResponse users = 1;
}

message Empty {}
```

`UserRequest` is what gRPC method will get in request.`UserResponse` is what gRPC method will return in response. `UserList` will be used to return the list of `UserResponse`. If any method does not take anything in request we will be using `Empty` message.

Let's create service or methods to in corporate the CRUD operations:
```proto
service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (UserRequest) returns (UserResponse);
  rpc UpdateUser (UserRequest) returns (UserResponse);
  rpc DeleteUser (UserRequest) returns (UserResponse);
  rpc ListUsers (Empty) returns (UserList);
}
```

As you can see GetUser is a method and it will take `UserRequest` as argument and return `UserResponse`. As we discussed earlier if any method doesn't need any argument it will take 
`Empty` message as an argument (check the `ListUser` method.)

Finally out `service.proto` file will look like:

```proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (UserRequest) returns (UserResponse);
  rpc UpdateUser (UserRequest) returns (UserResponse);
  rpc DeleteUser (UserRequest) returns (UserResponse);
  rpc ListUsers (Empty) returns (UserList);
}

message UserRequest {
  int32 id = 1;
  string name = 2;
  string email = 3;
  string phone_number = 4;
  bool is_active = 5;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  string phone_number = 4;
  bool is_active = 5;
}

message UserList {
    repeated UserResponse users = 1;
}

message Empty {}

```

Once you’ve specified your data structures, you use the protocol buffer compiler `protoc` to generate data access classes in your preferred language(s) from your proto definition. These provide simple accessors for each field, like name() and set_name(), as well as methods to serialize/parse the whole structure to/from raw bytes.

Use following command to generate python code:

```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto
```

Before running that command, make sure you have `grpc_tools` installed in your environment.

If not dont wory check out the github project link at the end of this article and create virtual environment with `requirement.txt` and then run this command.

This command will generate two files. `service_pb2_grpc.py` and `service_pb2.py`.

#### Generated Files:

##### service_pb2.py

Defines message classes for data serialization.

Example:

```python
import service_pb2

message = service_pb2.MyRequest(name="Alice")
serialized = message.SerializeToString()
deserialized = service_pb2.MyRequest.FromString(serialized)
```

##### service_pb2_grpc.py

Defines the gRPC service classes for client-server communication.

Includes:

1. `add_ServiceServicer_to_server()` → Registers the service on the server.

2. `ServiceStub` → A client stub for making RPC calls.

Example:

```python
import grpc
import service_pb2
import service_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = service_pb2_grpc.ServiceStub(channel)
response = stub.MyMethod(service_pb2.MyRequest(name="Alice"))
print(response.message)
```

Internals of these two files are beyond this discussion. You can refere official documentaion for that.

We unserstood everything needed for gRPC server. Now, creating a `server.py` which will be reponsible to start the server.

```python
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


```

After that our directory structure will looks like:

![Directory](dir_struct.png)

To start the server we can run simple command:
```
python server.py
```

If you see following message on console, we are ready to test this server.

```
gRPC server started on port 50051
```

To test the server just import the `service.proto` file on postment and try endpoints.

[![Testing])](testing_server.mp4)