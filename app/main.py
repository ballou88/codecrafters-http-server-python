import socket
from typing import List  # noqa: F401
import concurrent.futures


def main():
    HOST = "localhost"
    PORT = 4221
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        while True:
            conn, addr = server_socket.accept()
            print(f"New connection from {addr}")
            executor.submit(handle_connection, conn)


def handle_connection(conn):
    print("handling connection")
    data = conn.recv(1024).decode()
    req = parse_request(data)
    print(f"Recieved request: {req}")
    if req["path"] == "/":
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
    elif req["path"] == "/user-agent":
        response = generate_user_agent_response(req["headers"])
        conn.send(response.encode())
    elif req["path"].startswith("/echo/"):
        response = generate_echo_response(req["path"])
        conn.send(response.encode())
    else:
        conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


def parse_request(data):
    CLRF = "\r\n"
    output = {"method": "", "path": "", "version": "", "headers": {}, "body": ""}
    lines = data.split(CLRF)
    request_list = lines[0].split()
    output["method"] = request_list[0]
    output["path"] = request_list[1]
    output["version"] = request_list[2]
    # Parse headers
    index = 1
    while lines[index] != "":
        header = lines[index].split(":")
        output["headers"][header[0]] = header[1].lstrip()
        index += 1
    output["body"] = lines[index + 1]
    print(output)
    return output


def generate_user_agent_response(headers):
    length = len(headers["User-Agent"])
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{headers['User-Agent']}"


def generate_echo_response(path):
    string = path.split("/")[2]
    length = len(string)
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{string}"


if __name__ == "__main__":
    main()
