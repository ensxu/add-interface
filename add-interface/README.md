This little python script add interface name to static route for Cisco routers. Two files are needed:

1. ip_route.txt. It contains all the ip route statement from a Cisco router.
2. config.txt. It contains the whole config of the Cisco router. Actually ip_route.txt should be able to be generated from it.

The script parse the ip_route.txt file, find the name of the vrf (if it exists), and the IP address of next hop. Then it parse config.txt, find the matching interface name of next hop, then generate new ip route statements.
