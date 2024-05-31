import socket
from enum import Enum
import threading

class Response(Enum):
    OK = "HTTP/1.1 200 OK\r\n"
    NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
    ECHO = "HTTP/1.1 200 OK\r\n"

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

    response = f"{Response.NOT_FOUND.value}" if requestURL != "/" else f"{Response.OK.value}\r\n"
    if "echo" in requestURL:
        data = requestURL.strip("/").split("/")[1]
        response = f"{Response.ECHO.value}Content-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}"
    elif "/user-agent" == requestURL:
        if "User-Agent" not in headers:
            raise Exception("For /user-agent Endpoint, User Agent header is missing!")
        userAgentHeader = headers["User-Agent"]
        response = f"{Response.OK.value}Content-Type: text/plain\r\nContent-Length: {len(userAgentHeader)}\r\n\r\n{userAgentHeader}"

    connection.sendall(str.encode(response))

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept() 
        threading.Thread(target=handleRequest, args=(connection, address)).start()

           
if __name__ == "__main__":
    main()
