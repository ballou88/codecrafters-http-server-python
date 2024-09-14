class Request:
    def __init__(self, request) -> None:
        self.request = request
        self.headers = {}
        self.method = ""
        self.path = ""
        self.version = ""
        self.body = ""
        self.parse_request(request)

    def parse_request(self, data):
        lines = data.split("\r\n")
        self.method, self.path, self.version = lines[0].split()[0:3]
        # Parse headers
        index = 1
        while lines[index] != "":
            line = lines[index].split(":")
            name, value = line[0], ":".join(line[1:])
            if name == "Accept-Encoding":
                self.headers[name] = value.lstrip().split(", ")
            else:
                self.headers[name] = value.lstrip()
            index += 1
        self.body = lines[index + 1]
