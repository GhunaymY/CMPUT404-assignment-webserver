import socketserver
import os


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
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

'''
Status Codes:
405: "Not Allowed Response" 
404: "Not Found Response"
301: "Moved Permanently" 
200: "OK" 
'''

HOST, PORT = "localhost", 8080 #Define the host and port where the server will listen for incoming connections.

# Map file extensions to content types
CONTENT_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
}

# Create a custom request handler by inheriting from BaseRequestHandler
class MyWebServer(socketserver.BaseRequestHandler):
    #function to create an HTTP response
    def create_response(self, status_code, content_type, content):
        response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\nConnection: Closed\r\n\r\n{content}" # Construct an HTTP response with the specified status code, content type, and content
        return response

    # Handle incoming requests
    def handle(self):
        self.data = self.request.recv(1024).strip() # Receive data from the client and remove leading/trailing whitespace
        print("Got a request of: %s\n" % self.data)

        decoded_request = self.data.decode('utf-8') #Decode the received data as UTF-8 to work with it as text

        # Split the request into lines to extract the request line
        request_lines = decoded_request.split("\r\n")
        request_line = request_lines[0].split()
        method, path = request_line[0], request_line[1]

        # Check if the request method is not GET (Could be POST, PUT)
        if method != "GET":
            response = self.create_response(405, "text/html", "Method Not Allowed") #Throw the 405 Status Code. 
            self.request.sendall(bytearray(response, 'utf-8'))
            return

        file_path = "www" + path # Construct the full file path

        # Check if the file exists
        if not os.path.exists(file_path) or "../" in path:
            response = self.create_response(404, "text/html", "Page Not Found") #Throw the 404 Status Code. 
            self.request.sendall(bytearray(response, 'utf-8'))
            return

        # Check if the file is a directory
        #For the Requirement: The webserver can return index.html from directories (paths that end in /)
        if os.path.isdir(file_path):
            if not path.endswith("/"):
                # Perform a 301 redirect
                redirect_location = path + "/"
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {redirect_location}\r\n\r\n"
                self.request.sendall(bytearray(response, 'utf-8'))
                return
            file_path += "/index.html" # If the path ends with "/", append "index.html" to it

        # Determine the content type based on the file extension
        file_extension = os.path.splitext(file_path)[1]
        content_type = CONTENT_TYPES.get(file_extension, "text/html")

        # Read and send the file content
        with open(file_path, 'r') as f:
            content = f.read()
            response = self.create_response(200, content_type, content)
            self.request.sendall(bytearray(response, 'utf-8'))


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

