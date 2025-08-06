from abc import ABC, abstractmethod
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from requests import get

class Interface(ABC):
    @abstractmethod
    def __init__(self):
        self.Session: Session = None
        self.get = get

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

    def RetryConfig(self,
        RetryTimes: int = 5,
        StatuCodes: list[int] = [],
        BackoffFactor: float = 0.5,
        Disable: bool = False,
    ):
        RetryStrategy = Retry(
            total=RetryTimes,  # 最多重试 5 次
            status_forcelist=StatuCodes,  # 遇到这些状态码就重试
            backoff_factor=BackoffFactor  # 退避因子：重试间隔 = {backoff_factor} * (2^(重试计数-1))
        )
        zHTTPAdapter = HTTPAdapter(max_retries=RetryStrategy)
        zSession = Session()
        zSession.mount("http://", zHTTPAdapter)
        zSession.mount("https://", zHTTPAdapter)

        self.Session = zSession if not Disable else None
        self.get = self.Session.get if not Disable else get

    @abstractmethod
    def Explore(self,
        *,
        project_type: str = '', # 项目类型
        page: int = 1, # 页数
        limit: int = 10, # 返回数量限制
        offset: int = 0, # 偏移量
        version: str = '', # 游戏版本
        category: str = '', # 分类
        sort: str = '', # 排序方式
        **addtional: dict
    ) -> list[dict]:
        pass

    @abstractmethod
    def Search(self,
        *,
        query: str = '', # 搜索关键字
        project_type: str = '', # 项目类型
        page: int = 1, # 页数
        limit: int = 10, # 返回数量限制
        offset: int = 0, # 偏移量
        version: str = '', # 游戏版本
        category: str = '', # 分类
        sort: str = '', # 排序方式
        **addtional: dict
    ) -> list[dict]:
        pass

    @abstractmethod
    def Project(self, project_info: dict,
                      **addtional: dict) -> dict:
        pass

    @abstractmethod
    def Locate(self, project_info: dict,
                     versions: str | list[str] = '',
                     **addtional: dict) -> list[dict]:
        pass
