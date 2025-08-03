from Plugins.Interface_BASIC import Interface as Interface_Basic

class Interface(Interface_Basic): # 有反爬, 先不做
    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return 'Interface_CURSEFORGE'
    
    @property
    def version(self) -> str:
        return '0.1.0'

    @property
    def ptype(self) -> str:
        return 'Interface'

    @property
    def author(self) -> str:
        return 'NuhilLucas'
    
    @property
    def description(self) -> str:
        return 'CURSEFORGE 接口'

    def Explore(self, *,
                      project_type: str = '', # 项目类型
                      page: int = 1, # 页数
                      limit: int = 10, # 返回数量限制
                      offset: int = 0, # 偏移量
                      version: str = '', # 游戏版本
                      category: str = '', # 分类
                      sort: str = '', # 排序方式
                      **addtional: dict) -> list[dict]:
        pass

    def Search(self, *,
                     query: str = '', # 搜索关键字
                     project_type: str = '', # 项目类型
                     page: int = 1, # 页数
                     limit: int = 10, # 返回数量限制
                     offset: int = 0, # 偏移量
                     version: str = '', # 游戏版本
                     category: str = '', # 分类
                     sort: str = '', # 排序方式
                     **addtional: dict) -> list[dict]:
        pass

    def Project(self, project_info: dict,
                      **addtional: dict) -> dict:
        pass

    def Locate(self, project_info: dict,
                     versions: str | list[str] = '',
                     **addtional: dict):
        pass


def GetInterface() -> Interface:
    return Interface()
