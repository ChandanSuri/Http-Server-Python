import socket
from enum import Enum

class Response(Enum):
    OK = "HTTP/1.1 200 OK\r\n\r\n"
    NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
    ECHO = "HTTP/1.1 200 OK\r\n"

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() 

    with connection:
        while True:
            requestData = connection.recv(1024)
            requestParams = requestData.decode().split("\r\n")
            requestURL = requestParams[0].split(" ")[1]

            response = f"{Response.NOT_FOUND.value}" if requestURL != "/" else f"{Response.OK.value}"
            if "echo" in requestURL:
                data = requestURL.strip("/").split("/")[1]
                response = f"{Response.ECHO.value}Content-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}"

            connection.sendall(str.encode(response))


if __name__ == "__main__":
    main()
