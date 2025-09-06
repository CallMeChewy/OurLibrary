
import http.server
import socketserver
import json
import webbrowser
import os

def find_and_start_server():
    with open('Config/ourlibrary_config.json', 'r') as f:
        config = json.load(f)

    host = config.get('server_host', '127.0.0.1')
    ports = config.get('server_port_range', [8080, 8081, 8082, 3000, 8000, 8010, 8090, 5000, 9000])

    for port in ports:
        try:
            Handler = http.server.SimpleHTTPRequestHandler
            with socketserver.TCPServer((host, port), Handler) as httpd:
                url = f"http://{host}:{port}/new-desktop-library.html"
                print(f"Serving on {url}")
                webbrowser.open(url)
                httpd.serve_forever()
                return
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {port} is already in use. Trying next port.")
            else:
                raise e

    print("Could not find an available port.")

if __name__ == "__main__":
    find_and_start_server()
