from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import socket


"""
Class for mDNS. Will search for services on local network. 
"""

class mDNS():    

    """ 
    Searches for service by type and name on local network, within default 3 second timeout
    returns ipv4 address string, and int port
    """

    @staticmethod
    def serviceStatus(service, timeout = 3):

        if service != None and len(service) == 2: # checks that type and name exist

            zeroconf = Zeroconf()
            info = zeroconf.get_service_info(service[0], service[1]) # inputs service type, and name 

            if info: # found
                return ( (socket.inet_ntoa(info.addresses[0])) , info.port) # converts address from 32-bit binary to IPV4 string
            else: # not found
                return None, None
            zeroconf.close()