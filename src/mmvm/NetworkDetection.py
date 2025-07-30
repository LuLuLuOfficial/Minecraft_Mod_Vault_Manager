from requests import get
from typing import Literal
from requests import Response
from timeit import timeit

def ConnectionTest(Mode: Literal['IPv4', 'IPv6'], Times: int = 10):
    def DelayTest():
        try: get(API, timeout=5).raise_for_status()
        except: return 5

    match Mode:
        case 'IPv4':
            API: str = 'https://ipv4.icanhazip.com/'
        case 'IPv6':
            API: str = 'https://ipv6.icanhazip.com/'
        case _:
            raise ValueError('Invalid Mode')

    try:
        zResponse: Response = get(API)
        zResponse.raise_for_status()
    except Exception as E: return False
    else: return timeit(DelayTest, number=Times)/Times