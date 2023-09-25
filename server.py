#  coding: utf-8
import socket
import socketserver
from typing import List, Dict
import pathlib


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore, it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    request: socket.socket

    webroot: str = "www"
    NL: str = "\r\n"
    method: str
    path_str: str
    path: pathlib.Path
    fields: Dict[str, str] = dict()

    NOT_ALLOWED: str = "405 Method Not Allowed" + NL * 2
    NOT_FOUND: str = "404 Not Found" + NL * 2

    def set_fields(self, data: List[str]) -> None:
        self.fields.clear()
        for string in data:
            try:
                k, v = string.split(":", 1)
                self.fields[k] = v.strip()
            except ValueError:
                pass

    def get_field(self, key: str) -> str:
        return self.fields[key]

    def parse_request(self, data: bytes) -> None:
        # print(f"{data = }")
        temp = data.decode("utf8").split(self.NL)
        self.method = temp[0].split()[0]
        self.path_str = temp[0].split()[1]
        self.path = pathlib.Path(self.webroot + self.path_str)
        self.set_fields(temp[1:])
        # print(f"{self.method = }")
        # print(f"{self.path_str = }")
        # print(f"{self.path = }")
        # print(f"{self.fields = }")

    def validate_path(self) -> bool:
        webroot = pathlib.Path("www")
        path = pathlib.Path(str(webroot) + self.path_str)
        rel_path = path.relative_to(webroot)
        # print(f"{rel_path = }")
        if ".." in str(rel_path):
            return False
        return path.exists()

    def add_header(self, name: str, value: str) -> str:
        return f"{name}: {value}" + self.NL * 2

    def handle(self):
        # -- From documentation - https://docs.python.org/3/library/socketserver.html#examples --
        # self.request is the TCP socket connected to the client
        self.parse_request(self.request.recv(1024).strip())
        # print("{} wrote:".format(self.client_address[0]))
        # -- End --

        response: str = "HTTP/1.1 "
        if not self.method.startswith("GET"):
            response += self.NOT_ALLOWED
        elif not self.validate_path():
            response += self.NOT_FOUND
        else:
            response += self.valid_path_response()

        # print(f"{response = }")
        # print("-" * 10)
        self.request.sendall(bytearray(response, "utf-8"))

    def valid_path_response(self):
        response = ""
        if self.path.is_dir():
            if not self.path_str.endswith("/"):
                response += (
                    f"301 Moved Permanently{self.NL}Location: "
                    f"{'http://' + self.get_field('Host') + self.path_str}/"
                    + self.NL * 2
                )
            else:
                self.path = self.path.joinpath("index.html")
                response = self.get_file_contents(self.path, response)

        elif self.path.is_file():
            response = self.get_file_contents(self.path, response)
        return response

    def get_file_contents(self, path: pathlib.Path, response):
        try:
            f = open(path, "r")
            response += "200 OK" + self.NL
            response += self.add_header("Content-Type", f"text/{path.suffix[1:]}")
            response += f.read()
            response += self.NL * 2
            f.close()
        except:
            response += self.NOT_FOUND
        return response

    # def handle(self):
    #     self.
    #     self.data = self.request.recv(1024).strip()
    #     lines = decode(self.data)[0].split('{self.NL}')
    #     if !lines[0].startswith("GET "):
    #
    #     print("Got a request of: %s\n" % self.data)
    #     self.request.sendall(bytearray())
    #     self.request.sendall(bytearray("OK", "utf-8"))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()