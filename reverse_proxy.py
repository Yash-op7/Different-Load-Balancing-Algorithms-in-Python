import http.server
import socketserver
import urllib.request
import threading
import argparse
import hashlib
import redis

# List of backend servers
backend_servers = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]
backend_servers_loads = [0, 0, 0]             #! Initialize current loads for each server for testing 
backend_servers_response_times = [0, 0, 0]    #! Initialize response times for each server for testing, in real implementation they are dynamically fetched
client_to_server_mapping = {}
server_weights = [0.8, 0.1, 0.1]              #! List of weights for each backend server proportional to its computing power


class LoadBalancer:
    def select_server(self, key):
        raise NotImplementedError("select_server() must be implemented by subclasses")

class RoundRobinLoadBalancer(LoadBalancer):
    def __init__(self):
        self.server_index = 0
        self.index_lock = threading.Lock()

    def select_server(self, key):
        with self.index_lock:
            backend_server = backend_servers[self.server_index]
            self.server_index = (self.server_index + 1) % len(backend_servers)
        return backend_server

class StickyRoundRobinLoadBalancer(LoadBalancer):
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def select_server(self, client_ip):
        if client_ip in client_to_server_mapping:
            # If client has previously been assigned a server, use that server
            return client_to_server_mapping[client_ip]
        else:
            # Otherwise, use the next server in the round-robin sequence
            return self.round_robin()

    def round_robin(self):
        # Find the next available server in the round-robin sequence
        next_server = backend_servers[len(client_to_server_mapping) % len(backend_servers)]
        return next_server


class WeightedRoundRobinLoadBalancer(LoadBalancer):
    def __init__(self):
        self.weighted_servers = self.generate_weighted_servers()

    def generate_weighted_servers(self):
        weighted_servers = []
        for server, weight in zip(backend_servers, server_weights):
            weighted_servers.extend([server] * int(weight * 10))
        return weighted_servers

    def select_server(self):
        return random.choice(self.weighted_servers)

class IPHashedLoadBalancer(LoadBalancer):
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.count = 0

    def select_server(self, key):
        # print("key is -> ", key)
        server = self.redis_client.get(key)
        if server is None:
            server = self.calculate_server(key)
            self.redis_client.set(key, server)
        return server.decode('utf-8')

    def calculate_server(self, key):
        # hash_value = hashlib.sha1(key.encode()).hexdigest()
        # server_index = int(hash_value, 16) % len(backend_servers)
        count+=1
        server_index = count % len(backend_servers)
        return backend_servers[server_index]
    
class LeastLoadedLoadBalancer(LoadBalancer):
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def select_server(self):
        min_load = min(range(len(backend_servers_loads)), key=lambda x: backend_servers_loads[x])
        return backend_servers[min_load]

class ResponseTimeLoadBalancer(LoadBalancer):
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def select_server(self):
        min_response_time = min(backend_servers_response_times)
        min_response_time_server_index = backend_servers_response_times.index(min_response_time)
        return backend_servers[min_response_time_server_index]
    



class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, load_balancer=None, **kwargs):
        self.load_balancer = load_balancer
        super().__init__(*args, **kwargs)

    def do_GET(self):
        client_ip = self.client_address[0]
        backend_server = self.load_balancer.select_server(client_ip)
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
    parser.add_argument('--lb_algorithm', type=str, choices=['rr1', 'ip_hashed', 'least_loaded', 'sticky_round_robin', 'weighted_round_robin'], default='rr1',
                        help='Load balancing algorithm to use (default: rr1 for round robin)')
    args = parser.parse_args()

    if args.lb_algorithm == 'rr1':
        load_balancer = RoundRobinLoadBalancer()
    elif args.lb_algorithm == 'ip_hashed':
        load_balancer = IPHashedLoadBalancer()
    elif args.lb_algorithm == 'least_loaded':
        load_balancer = LeastLoadedLoadBalancer()
    elif args.lb_algorithm == 'sticky_round_robin':
        load_balancer = StickyRoundRobinLoadBalancer()
    elif args.lb_algorithm == 'weighted_round_robin':
        load_balancer = WeightedRoundRobinLoadBalancer()
    else:
        raise ValueError(f"Unsupported load balancing algorithm: {args.lb_algorithm}")

    run(load_balancer=load_balancer)
