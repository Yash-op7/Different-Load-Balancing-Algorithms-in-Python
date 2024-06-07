import http.server
import socketserver
import urllib.request
import threading
import argparse

# List of backend servers
backend_servers = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]

class LoadBalancer:
    def __init__(self):
        self.server_index = 0
        self.index_lock = threading.Lock()

    def select_server(self):
        raise NotImplementedError("select_server() must be implemented by subclasses")

class RoundRobinLoadBalancer(LoadBalancer):
    def select_server(self):
        with self.index_lock:
            backend_server = backend_servers[self.server_index]
            self.server_index = (self.server_index + 1) % len(backend_servers)
        return backend_server

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, load_balancer=None, **kwargs):
        self.load_balancer = load_balancer
        super().__init__(*args, **kwargs)

    def do_GET(self):
        backend_server = self.load_balancer.select_server()
        url = f"{backend_server}{self.path}"
        self.send_proxy_request(url)

    def send_proxy_request(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                self.send_response(response.getcode())
                self.send_headers(response.info())
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error forwarding request: {e}")

    def send_headers(self, headers):
        for key, value in headers.items():
            if key.lower() == 'transfer-encoding' and value.lower() == 'chunked':
                continue
            self.send_header(key, value)
        self.end_headers()

def run(server_class=http.server.HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080, load_balancer=None):
    server_address = ('', port)
    httpd = server_class(server_address, lambda *args, **kwargs: handler_class(*args, load_balancer=load_balancer, **kwargs))
    print(f"Reverse proxy server running on port {port} with load balancing algorithm: {type(load_balancer).__name__}")
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reverse Proxy Load Balancer')
    parser.add_argument('--lb_algorithm', type=str, choices=['rr1'], default='rr1',
                        help='Load balancing algorithm to use (default: rr1 for round robin)')
    args = parser.parse_args()

    if args.lb_algorithm == 'rr1':
        load_balancer = RoundRobinLoadBalancer()
    else:
        raise ValueError(f"Unsupported load balancing algorithm: {args.lb_algorithm}")

    run(load_balancer=load_balancer)
