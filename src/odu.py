# MIT License
#
# Copyright (c) 2024 Fontivan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
odu.py is used to provided a temporary file download secured behind
a random port, random uuid, and a user provided password.
"""

import argparse
import http.server
from posixpath import basename
from random import randrange
import socketserver
import threading
import time
import uuid

import netifaces
import requests

class FileServerHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom request handler for the FileServer class.
    """
    # pylint: disable=C0103
    def do_GET(self):
        """
        Handle HTTP GET requests.
        """
        try:
            _, uuid_str, password = self.path.split('/', 2)
            uuid.UUID(uuid_str)
            if uuid_str.strip() == str(self.server.secret_uuid_path).strip() and password.strip() == self.server.password:
                with open(self.server.file_path, 'rb') as file:
                    filename = basename(self.server.file_path)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.end_headers()
        except ValueError:
            self.send_response(404)
            self.end_headers()

class FileServer(socketserver.TCPServer):
    """
    Custom TCP server for serving files with a secret UUID path.
    """
    # pylint: disable=R0913
    def __init__(self, server_address, handler_class, file_path, secret_uuid_path, password):
        self.file_path = file_path
        self.secret_uuid_path = secret_uuid_path
        self.password = password
        super().__init__(server_address, handler_class)

def run_server(port, file_path, secret_uuid_path, max_wait_period_hours, password):
    """
    Run the HTTP server to serve the specified file and automatically shut down after a maximum wait period.
    """
    server_address = ('', port)
    httpd = FileServer(server_address, FileServerHandler, file_path, secret_uuid_path, password)
    def wait_and_shutdown():
        print(f"Waiting up to {max_wait_period_hours} hours before exiting automatically")
        time.sleep(max_wait_period_hours * 3600)
        httpd.shutdown()
        print("Shutting down due to reaching wait limit")
        raise SystemExit
    # Exit only if zero or negative time was specified
    if max_wait_period_hours > 0:
        shutdown_thread = threading.Thread(target=wait_and_shutdown)
        shutdown_thread.daemon = True
        shutdown_thread.start()
    httpd.serve_forever()

def get_lan_ip():
    """
    Get the LAN IP address of the machine.
    """
    try:
        if not hasattr(netifaces, 'interfaces'):
            print("netifaces module does not have 'interfaces' attribute")
            return None

        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses and not interface.startswith("lo"):
                return addresses[netifaces.AF_INET][0]['addr']

        # Return None if no suitable IP address is found
        return None

    except AttributeError as e:
        print("AttributeError:", e)
        return None

def get_external_ip_address(ip_fetch_host):
    """
    Retrieve the external IP address from the specified hostname.
    """
    ip = requests.get(ip_fetch_host, timeout=30).content.decode('utf8')
    return ip

def parse_args():
    """
    Parse command-line arguments and return the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Argument parser for odu")

    parser.add_argument(
        "--max-wait-period-hours",
        type=int,
        default=1,
        help="Max wait time before exiting (default: 1). Set to 0 or -1 to disable automatic shutdown."
    )

    parser.add_argument(
        "--port",
        type=int,
        default=randrange(10000, 65535, 1),
        help="Port for the HTTP server (default: random)"
    )

    parser.add_argument(
        "--ip-fetch-host",
        type=str,
        default="https://api.ipify.org",
        help="Hostname to check for the external IP address (default: 'https://api.ipify.org')"
    )

    parser.add_argument(
        "--file-path",
        type=str,
        default=None,
        required=True,
        help="Path to the file to be served (required)"
    )

    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password required for file download (required)"
    )

    args = parser.parse_args()
    return args

def main():
    """
    Main function to start the file server and print server information.
    """
    args = parse_args()
    external_ip_address = get_external_ip_address(args.ip_fetch_host)
    local_ip_address = get_lan_ip()
    secret_path_uuid = uuid.uuid4()
    print(f"File '{args.file_path}' is now available at 'http://{external_ip_address}:{args.port}/{secret_path_uuid}/{args.password}'")
    print(f"File '{args.file_path}' is now available at 'http://{local_ip_address}:{args.port}/{secret_path_uuid}/{args.password}'")
    print(f"File '{args.file_path}' is now available at 'http://127.0.0.1:{args.port}/{secret_path_uuid}/{args.password}'")
    print("Remember to configure firewall or network router ports!")
    run_server(args.port, args.file_path, secret_path_uuid, args.max_wait_period_hours, args.password)

if __name__ == '__main__':
    main()
