# Different-Load-Balancing-Algorithms-in-Python
Implemented 6 different load balancing algorithms which redirect incoming loads using a reverse proxy server in Python.
The six algorithms are:
1. Round Robin
2. Sticky Round Robin
3. Weighted Round Robin
4. IP hash
5. Least Connections
6. Least Response Time

To run the application, first run the backend servers, like so:

# Terminal 1
python3 -m http.server 8001

# Terminal 2
python3 -m http.server 8002

# Terminal 3
python3 -m http.server 8003

Then start redis server in a new terminal with the following command:
redis-server

Make sure it is running on the default port of 6379

Then the different instances of the reverse proxy can be invoked via the following commands:
1. python3 reverse_proxy.py --lb_algorithm='rr_simple'
2. python3 reverse_proxy.py --lb_algorithm='rr_sticky'
3. python3 reverse_proxy.py --lb_algorithm='rr_weighted'
4. python3 reverse_proxy.py --lb_algorithm='ip_hash'
5. python3 reverse_proxy.py --lb_algorithm='least_conns'
6. python3 reverse_proxy.py --lb_algorithm='least_response_time'

You can then curl this reverse proxy server to see the load balancing algorithm in action:

curl http://localhost:8080
