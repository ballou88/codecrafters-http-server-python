import socket
import argparse
import os.path
import concurrent.futures
from .request import Request
from .response import Response


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
    data = conn.recv(1024).decode()
    req = Request(data)
    response = handle_request(req)
    conn.sendall(response)


def handle_request(req):
    response = Response()
    # if req is None:
    #     response.status = 500
    #     return response.out()
    if req.method == "GET":
        if req.path == "/":
            response.status = 200
        elif req.path == "/user-agent":
            response.status = 200
            response.body = req.headers["User-Agent"]
            response.content_type = "text/plain"
        elif req.path.startswith("/echo/"):
            string = req.path.split("/")[2]
            if "Accept-Encoding" in req.headers:
                response.accept_encoding = req.headers["Accept-Encoding"]
            response.status = 200
            response.content_type = "text/plain"
            response.body = string
        elif req.path.startswith("/files/"):
            data = load_file(req)
            if data:
                response.status = 200
                response.content_type = "application/octet-stream"
                response.body = data
            else:
                response.status = 404
        else:
            response.status = 404
    elif req.method == "POST":
        if req.path.startswith("/files/"):
            handle_file_create(req)
            response.status = 201
    return response.generate()


def handle_file_create(req):
    file_name = req.path.split("/")[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", dest="directory")
    args = parser.parse_args()
    file_path = args.directory + file_name
    with open(file_path, "w") as f:
        f.write(req.body)


def load_file(req):
    file_name = req.path.split("/")[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", dest="directory")
    args = parser.parse_args()
    file_path = args.directory + file_name
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            data = f.read()
        return data
    else:
        return None


if __name__ == "__main__":
    main()
