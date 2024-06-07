# Different-Load-Balancing-Algorithms-in-Python
Implemented 6 different load balancing algorithms in Python using a reverse proxy server.
The six algorithms are:
1. Round Robin
2. Sticky Round Robin
3. Weighted Round Robin
4. IP hash
5. Least Connections
6. Least Response Time


The different instances of the reverse proxy can be invoked via the following commands:
1. python3 reverse_proxy.py --lb_algorithm='rr_simple'
2. python3 reverse_proxy.py --lb_algorithm='rr_sticky'
3. python3 reverse_proxy.py --lb_algorithm='rr_weighted'
4. python3 reverse_proxy.py --lb_algorithm='ip_hash'
5. python3 reverse_proxy.py --lb_algorithm='least_conns'
6. python3 reverse_proxy.py --lb_algorithm='least_response_time'
