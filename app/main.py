import socket
import gzip
import binascii
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
        if header[0] == "Accept-Encoding":
            output["headers"][header[0]] = header[1].lstrip().split(", ")
        else:
            output["headers"][header[0]] = header[1].lstrip()
        index += 1
    output["body"] = lines[index + 1]
    return output


def handle_connection(conn):
    print("handling connection")
    data = conn.recv(1024).decode()
    req = parse_request(data)
    if req is None:
        res_data = {"status": 500}
        conn.send(build_response(res_data))
        return
    print(f"Recieved request: {req}")
    res_data = {}
    if req["method"] == "GET":
        if req["path"] == "/":
            res_data = {"status": 200}
        elif req["path"] == "/user-agent":
            res_data = generate_user_agent_response(req)
        elif req["path"].startswith("/echo/"):
            res_data = generate_echo_response(req)
        elif req["path"].startswith("/files/"):
            res_data = generate_file_response(req)
        else:
            res_data = {"status": 404}
    elif req["method"] == "POST":
        if req["path"].startswith("/files/"):
            res_data = handle_file_create(req)
    conn.send(build_response(res_data))


def build_response(res_data):
    RESPONSE = {200: "200 OK", 201: "201 Created", 404: "404 Not Found"}
    response = [f"HTTP/1.1 {RESPONSE[res_data['status']]}"]
    if "Content-Type" in res_data:
        response.append(f"Content-Type: {res_data['Content-Type']}")
    if "Content-Length" in res_data:
        response.append(f"Content-Length: {res_data['Content-Length']}")
    if "Content-Encoding" in res_data:
        response.append(f"Content-Encoding: {res_data['Content-Encoding']}")
    out = "\r\n".join(response) + "\r\n\r\n"
    if res_data.get("body"):
        out = out.encode() + bytes(res_data["body"])
    else:
        out = out.encode()
    print(out)
    return out


def handle_file_create(req):
    file_name = req["path"].split("/")[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", dest="directory")
    args = parser.parse_args()
    file_path = args.directory + file_name
    with open(file_path, "w") as f:
        f.write(req["body"])
    return {"status": 201}


def generate_file_response(req):
    file_name = req["path"].split("/")[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", dest="directory")
    args = parser.parse_args()
    file_path = args.directory + file_name
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            data = f.read()
        res_data = {
            "status": 200,
            "Content-Type": "application/octet-stream",
            "body": data.encode(),
            "Content-Length": len(data),
        }
        return res_data
    else:
        return {"status": 404}


def generate_user_agent_response(req):
    return {
        "status": 200,
        "body": req["headers"]["User-Agent"].encode(),
        "Content-Type": "text/plain",
        "Content-Length": len(req["headers"]["User-Agent"]),
    }


def generate_echo_response(req):
    string = req["path"].split("/")[2]
    res_data = {
        "status": 200,
        "Content-Type": "text/plain",
        "body": string.encode(),
        "Content-Length": len(string.encode()),
    }
    if "Accept-Encoding" in req["headers"]:
        encodings = req["headers"]["Accept-Encoding"]
        for encoding in encodings:
            if encoding in ["gzip"]:
                res_data["body"] = gzip.compress(string.encode())
                res_data["Content-Encoding"] = encoding
                res_data["Content-Length"] = len(res_data["body"])
    return res_data


if __name__ == "__main__":
    main()
