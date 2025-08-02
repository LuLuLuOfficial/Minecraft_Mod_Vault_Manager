from requests import get as _requests_get_
from requests.models import Response as _Response_
from aiohttp import ClientSession as _ClientSession_
from asyncio import gather as _asyncio_gather_
from asyncio import run as _asyncio_run_
# 假设 Plugins.Interface_Example.Interface 存在
# from Plugins.Interface_Example import Interface as _BaseInterface_

# ... (APIs, GetProjectType, GetSortTypes, GetGameVersions, GetCategories, GetLoaders, GetSideTypes 函数保持不变) ...

# 修改后的 Interface 类
class Interface(): # 假设它继承自某个基类 _BaseInterface_
    def __init__(self):
        # 注意：这里不进行异步操作
        self.project_types: dict = None
        self.sort_types: dict = None
        self.versions: dict = None
        self.categories: dict = None
        self.loaders: dict = None
        self.side_types: dict = None
        # self.query_types: dict = None # 代码中未定义

    async def async_init(self):
        """异步初始化方法，用于获取所有数据并赋值"""
        # ... (async_init 的内容保持不变) ...
        async with _ClientSession_() as session:
            (
                self.project_types,
                self.sort_types,
                self.versions,
                self.categories,
                self.loaders,
                self.side_types
            ) = await _asyncio_gather_(
                GetProjectType(session),
                GetSortTypes(session),
                GetGameVersions(session),
                GetCategories(session),
                GetLoaders(session),
                GetSideTypes(session)
            )
        return self # 支持链式调用

    # 新增类方法，用于创建并初始化实例
    @classmethod
    async def create(cls) -> 'Interface':
        """异步创建并初始化 Interface 实例"""
        instance = cls()
        await instance.async_init()
        return instance

    # 如果你仍然想提供一个同步方式来获取实例化对象，可以保留或修改 GetInterface 风格的函数
    @classmethod
    def get_instance(cls) -> 'Interface':
        """同步方式获取完全初始化的实例"""
        async def _create_instance():
            return await cls.create()
        return _asyncio_run_(_create_instance())

    # ... (name, version, ptype, author, description 属性 和 Explore, Search, Project, Locate 方法 保持不变) ...

# --- 使用方法 ---

# 方法 1: 使用类方法 create (需要在 async 环境中)
# async def main():
#     interface_instance = await Interface.create()
#     # 现在 interface_instance 已经初始化完成
#     print(interface_instance.project_types)

# # 运行异步主函数
# _asyncio_run_(main())


# 方法 2: 使用类方法 get_instance (同步方式，内部使用 asyncio.run)
interface_instance = Interface.get_instance()
# 现在 interface_instance 已经初始化完成
print(interface_instance.project_types)
