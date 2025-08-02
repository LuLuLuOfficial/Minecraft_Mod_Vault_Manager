from abc import ABC, abstractmethod

class Interface(ABC):
    @abstractmethod
    def __init__(self):
        self.project_types: dict
        
        self.sort_types: dict

        self.versions: set
        
        self.categories: dict

        self.loaders: dict

        self.side_types: dict
        
        self.query_types: dict

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def ptype(self) -> str:
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def Project(self, project_info: dict,
                      **addtional: dict) -> dict:
        pass

    @abstractmethod
    def Locate(self, project_info: dict,
                     versions: str | list[str] = '',
                     **addtional: dict):
        pass
