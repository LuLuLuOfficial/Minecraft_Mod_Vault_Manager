from mmvm.Public.LogManager import LogManager

from typing import Literal
from requests import get
from timeit import timeit
from socket import socket, AF_INET, AF_INET6, AddressFamily, SOCK_STREAM

def IPvConnectTest(Mode: Literal['IPv4', 'IPv6'], Timeout: int = 5):
    IPv_host: str # Google Public DNS IPv6 / IPv4 地址
    Port: int # DNS 端口，通常开放
    Family: AddressFamily | int = -1,
    match Mode:
        case 'IPv4':
            IPv_host = "8.8.8.8"
            Port = 53
            Family = AF_INET
        case 'IPv6':
            IPv_host = "2001:4860:4860::8888"
            Port = 53
            Family = AF_INET6

    try:
        Sock = socket(Family, SOCK_STREAM)
        Sock.settimeout(Timeout)
        Sock.connect((IPv_host, Port))
        Sock.close()
    except Exception as e:
        LogManager(f"❌ {Mode} Connect Test Failed: {e}")
        return False
    else:
        LogManager(f"✅ {Mode} Connect Test Succeed")
        return True

def ConnectionTest(Mode: Literal['IPv4', 'IPv6'], Times: int = 10, Timeout: int = 5):
    def DelayTest():
        try: get(url=API, timeout=Timeout).raise_for_status()
        except: return

    match Mode:
        case 'IPv4':
            API: str = 'https://ipv4.icanhazip.com/'
        case 'IPv6':
            API: str = 'https://ipv6.icanhazip.com/'
        case _:
            raise ValueError('Invalid Mode')

    if any([IPvConnectTest(Mode, Timeout) for _ in range(Times)]):
        return timeit(DelayTest, number=Times)/Times
    else:
        return False

if __name__ == '__main__':
    IPvConnectTest('IPv4', 5)
    IPvConnectTest('IPv6', 5)
    print(ConnectionTest('IPv4', 3, 2))
    print(ConnectionTest('IPv6', 3, 2))
