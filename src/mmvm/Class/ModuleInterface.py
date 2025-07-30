class ModuleInterface():
    def __init__(self):
        self.version: str
        self.name: str
        self.author: str
        self.Interface: callable
        self.GetInterface: callable

class Interface():
    def __init__(self):
        self.project_types: dict
        
        self.sort_types: dict

        self.versions: set
        
        self.categories: dict

        self.loaders: dict

        self.side_types: dict
        
        self.query_types: dict

    def Explore(self, *,
                      project_type: str = '', # 项目类型
                      page: int = 1, # 页数
                      limit: int = 10, # 返回数量限制
                      offset: int = 0, # 偏移量
                      version: str = '', # 游戏版本
                      category: str = '', # 分类
                      sort: str = '', # 排序方式
                      **addtional: dict):
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
                     **addtional: dict):
        pass
