from requests import get
from requests.models import Response
from typing import Any, Literal

PROJECT_TYPE = Literal['mod', 'modpack', 'resourcepack', 'shader']
GAME_VERSION = Literal['1.7.10', '1.12.2', '1.16.5', '1.18.2', '1.19.2', '1.20.1', '1.20.4', '1.21']
MOD_LOADER = Literal['forge', 'fabric', 'quilt', 'neoforge', 'liteloader', 'rift']
RUN_SIDE = Literal['client_side', 'server_side', 'both_side', 'client_side_main', 'server_side_main']

class Scraper():
    def __init__(self):
        pass

    def Explore(self, sort: str,
                      page: int = 1,
                      offset: int = 0,
                      type: PROJECT_TYPE | None = None,
                      loader: MOD_LOADER | None = None,
                      version: GAME_VERSION | None = None,
                      facets: dict | str | None = None,) -> tuple[list, dict] | None: # data, metadata
        pass

    def Search(self, query: str,
                     sort: str | None = None,
                     page: int = 1,
                     offset: int = 0,
                     type: PROJECT_TYPE | None = None,
                     loader: MOD_LOADER | None = None,
                     version: GAME_VERSION | None = None,
                     facets: dict | str | None = None,) -> tuple[list, dict]: # data, metadata
        pass

class Scrper_MCMOD(Scraper):
    def __init__(self):
        super().__init__()

    def Explore(self, sort: Literal['createtime', 'lastedittime'] | None = None,
                      page: int = 1,
                      offset: int = 0,
                      type: PROJECT_TYPE | None = None,
                      loader: MOD_LOADER | Literal['数据包','行为包','命令方块','文件覆盖'] | None = None,
                      version: GAME_VERSION | None = None,
                      facets: dict | str | None = None,) -> tuple[list, dict] | None: # data, metadata
        """_summary_

        Args:
            sort (Literal['createtime', 'lastedittime'] | None, optional): _description_. Defaults to None.
            page (int, optional): _description_. Defaults to 1.
            offset (int, optional): _description_. Defaults to 0.
            type (PROJECT_TYPE | None, optional): _description_. Defaults to None.
            loader (MOD_LOADER | Literal['数据包','行为包','命令方块','文件覆盖'] | None): 'forge':1, 'fabric':2, 'quilt':11, 'neoforge':13, 'rift':3, 'liteloader':4, '数据包':5, '行为包':8, '命令方块':6, '文件覆盖':7.
            version (str | None, optional): _description_. Defaults to None.
            facets (dict | str | None, optional): _description_. Defaults to None.

        Returns:
            tuple[list, dict] | None: _description_
        """

        URL: str = f'https://www.mcmod.cn/modlist.html?platform=1&page={page}'
        if sort:
            URL += f'&sort={sort}'
        if loader:
            loader = {'forge':1,'fabric':2,'quilt':11,'neoforge':13,'rift':3,'liteloader':4,'数据包':5,'行为包':8,'命令方块':6,'文件覆盖':7}[loader]
            URL += f'&type={loader}'
        if version:
            URL += f'&mcver={version}'

        zResponse: Response = get(URL)
        if zResponse.status_code != 200: return None


    # def Search(self, query: str,
    #                  sort: str | None = None,
    #                  page: int = 1,
    #                  offset: int = 0,
    #                  facets: dict | str | None = None,) -> tuple[list, dict] | None:
    #     URL: str = f'https://search.mcmod.cn/s?filter=1&key={query}&page={page}' # filter=1: 仅搜索 Mod
    #     zResponse: Response = get(URL)
    #     if zResponse.status_code != 200: return None
        
if __name__ == '__main__':
    scraper = Scrper_MCMOD()
    result = scraper.Search('Carpet')
