import socket
import argparse
import os.path
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
        res_data = {"status": 200}
        conn.send(build_response(res_data))
    elif req["path"] == "/user-agent":
        response = generate_user_agent_response(req["headers"])
        conn.send(response.encode())
    elif req["path"].startswith("/echo/"):
        response = generate_echo_response(req["path"])
        conn.send(response.encode())
    elif req["path"].startswith("/files/"):
        response = generate_file_response(req["path"])
        conn.send(response.encode())
    else:
        res_data = {"status": 404}
        conn.send(build_response(res_data))


def build_response(res_data):
    RESPONSE = {200: "200 OK\r\n", 404: "404 Not Found\r\n"}
    response = f"HTTP/1.1 {RESPONSE[res_data['status']]}"
    if "Content-Type" in res_data:
        response += " " + res_data["Content-Type"]
    response += "\r\n"
    return response.encode()


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


def generate_response(body):
    length = len(body)
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{body}"


def generate_file_response(path):
    file_name = path.split("/")[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", dest="directory")
    args = parser.parse_args()
    file_path = args.directory + file_name
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            data = f.read()
        return generate_response(data)
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\n"


def generate_user_agent_response(headers):
    return generate_response(headers["User-Agent"])


def generate_echo_response(path):
    string = path.split("/")[2]
    return generate_response(string)


if __name__ == "__main__":
    main()
