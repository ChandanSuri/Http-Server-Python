import socket
from enum import Enum
import threading
import sys

class Response(Enum):
    OK = "HTTP/1.1 200 OK\r\n"
    NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
    ECHO = "HTTP/1.1 200 OK\r\n"

class ContentType(Enum):
    PLAIN_TEXT = "Content-Type: text/plain"
    APP_FILE = "Content-Type: application/octet-stream"

def parseRequestParams(requestParams):
    headers, body = {}, {}

    requestLineParams = requestParams[0].split(" ")
    if len(requestLineParams) < 3:
        raise Exception("Request is not well formed!")
    
    requestLine = {
        "requestType": requestLineParams[0],
        "requestUrl": requestLineParams[1],
        "httpVersion": requestLineParams[2]
    }

    headerEndIdx = 1
    for idx in range(1, len(requestParams)):
        headerParam = requestParams[idx]
        if headerParam == '':
            headerEndIdx = idx
            break

        headerParamsList = headerParam.split(" ")
        headers[headerParamsList[0].strip(":")] = headerParamsList[1]

    bodyIdx = headerEndIdx + 1
    if requestParams[bodyIdx] != '':
        body['body'] = requestParams[bodyIdx]

    return requestLine, headers, body

def handleRequest(connection, address):
    requestData = connection.recv(1024)
    requestParams = requestData.decode().split("\r\n")
    requestLine, headers, body = parseRequestParams(requestParams)
    requestURL = requestLine["requestUrl"]

    if requestURL == "/":
        response = f"{Response.OK.value}\r\n"
    elif requestURL.startswith("/echo"):
        data = requestURL.strip("/").split("/")[1]
        response = f"{Response.ECHO.value}{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(data)}\r\n\r\n{data}"
    elif requestURL.startswith("/user-agent"):
        if "User-Agent" not in headers:
            raise Exception("For /user-agent Endpoint, User Agent header is missing!")
        userAgentHeader = headers["User-Agent"]
        response = f"{Response.OK.value}{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(userAgentHeader)}\r\n\r\n{userAgentHeader}"
    elif requestURL.startswith("/files"):
        directoryName = sys.argv[2]
        fileName = requestURL[7:]
        try:
            with open(f"/{directoryName}/{fileName}", "r") as file:
                fileContents = file.read()
            response = f"{Response.OK.value}{ContentType.APP_FILE.value}\r\nContent-Length: {len(fileContents)}\r\n\r\n{fileContents}"
        except Exception as e:
            response = f"{Response.NOT_FOUND.value}"
    else:
        response = f"{Response.NOT_FOUND.value}"

    connection.sendall(str.encode(response))

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept() 
        threading.Thread(target=handleRequest, args=(connection, address)).start()

           
if __name__ == "__main__":
    main()
