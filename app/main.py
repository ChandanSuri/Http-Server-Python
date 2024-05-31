import socket
from enum import Enum
import threading
import sys
import gzip

class Response(Enum):
    OK = "HTTP/1.1 200 OK\r\n"
    NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
    CREATED = "HTTP/1.1 201 Created\r\n\r\n"

class ContentType(Enum):
    PLAIN_TEXT = "Content-Type: text/plain"
    APP_FILE = "Content-Type: application/octet-stream"


def parseRequestParams(requestParams):
    headers = {}

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

        headerParamsList = headerParam.split(": ")
        headers[headerParamsList[0]] = headerParamsList[1]

    bodyIdx = headerEndIdx + 1
    body = ""
    if requestParams[bodyIdx] != '':
        body = requestParams[bodyIdx]

    return requestLine, headers, body

def handleEchoRequest(requestURL, headers):
    compressedData = None
    data = requestURL.strip("/").split("/")[1]
    if "Accept-Encoding" in headers:
        acceptedEncodings = headers["Accept-Encoding"].split(", ")
        if any(map(lambda enc: enc == "gzip", acceptedEncodings)):
            compressedData = gzip.compress(data.encode())
            response = f"{Response.OK.value}Content-Encoding: gzip\r\n" + \
                f"{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(compressedData)}\r\n\r\n"
        else:
            response = f"{Response.OK.value}{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(data)}\r\n\r\n{data}"
    else:
        response = f"{Response.OK.value}{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(data)}\r\n\r\n{data}"

    return response, compressedData

def handleUserAgentRequest(headers):
    if "User-Agent" not in headers:
            raise Exception("For /user-agent Endpoint, User Agent header is missing!")
    userAgentHeader = headers["User-Agent"]
    response = f"{Response.OK.value}{ContentType.PLAIN_TEXT.value}\r\nContent-Length: {len(userAgentHeader)}\r\n\r\n{userAgentHeader}"

    return response

def handleFileRequests(requestURL, requestLine, body):
    directoryName = sys.argv[2]
    fileName = requestURL[7:]
    requestType = requestLine["requestType"]
    if requestType.upper() == "GET":
        try:
            with open(f"/{directoryName}/{fileName}", "r") as file:
                fileContents = file.read()
            response = f"{Response.OK.value}{ContentType.APP_FILE.value}\r\nContent-Length: {len(fileContents)}\r\n\r\n{fileContents}"
        except Exception as e:
            response = f"{Response.NOT_FOUND.value}"
    elif requestType.upper() == "POST":
        try:
            print(directoryName, fileName)
            with open(f"{directoryName}{fileName}", "w") as outFile:
                fileContents = outFile.write(body)
            response = f"{Response.CREATED.value}"
        except Exception as e:
            response = f"{Response.NOT_FOUND.value}"
    else:
        raise Exception(f"{requestType} not supported for a file!!!")
    
    return response

def handleRequest(connection, address):
    requestData = connection.recv(1024)
    requestParams = requestData.decode().split("\r\n")
    requestLine, headers, body = parseRequestParams(requestParams)
    requestURL = requestLine["requestUrl"]
    compressedData = None

    if requestURL == "/":
        response = f"{Response.OK.value}\r\n"
    elif requestURL.startswith("/echo"):
        response, compressedData = handleEchoRequest(requestURL, headers)
    elif requestURL.startswith("/user-agent"):
        response = handleUserAgentRequest(headers)
    elif requestURL.startswith("/files"):
        response = handleFileRequests(requestURL, requestLine, body)
    else:
        response = f"{Response.NOT_FOUND.value}"

    if compressedData is not None:
        connection.sendall(str.encode(response) + compressedData)
        return
    
    connection.sendall(str.encode(response))


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept() 
        threading.Thread(target=handleRequest, args=(connection, address)).start()

           
if __name__ == "__main__":
    main()
