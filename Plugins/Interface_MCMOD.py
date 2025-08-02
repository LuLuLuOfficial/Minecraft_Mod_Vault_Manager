from requests import get as _requests_get_
from requests.models import Response as _Response_
from re import search as _re_search_
from mmvm.Class.HTMLProcessor import FormatHTML as _FormatHTML_
from mmvm.Class.HTMLProcessor import HTMLElement as _HTMLElement_
from mmvm.Public.Instances import LogManager
from Plugins.Interface_Basic import Interface as Interface_Basic

version: str = '0.1.0'
name: str = 'Interface_MCMOD'
author: str = 'NuhilLucas'

class Interface(): # 基本好了, 要做一下 __init__ 方法里面数据的自动化获取
    def __init__(self):
        self.project_types: dict = {'mod': 'modlist',
                                    'modpack': 'modpack'}

        self.sort_types: dict = {'_default_': None,
                                 'time_create': 'createtime',
                                 'time_lastedit': 'lastedittime'}

        self.versions: set = {'_all_': None, '远古版本': 'earlier', 
                              '1.21.x': '1.21.x', '1.21.7': '1.21.7', '1.21.6': '1.21.6', '1.21.5': '1.21.5', '1.21.4': '1.21.4',
                              '1.21.3': '1.21.3', '1.21.2': '1.21.2', '1.21.1': '1.21.1', '1.21': '1.21', '1.20.x': '1.20.x',
                              '1.20.6': '1.20.6', '1.20.5': '1.20.5', '1.20.4': '1.20.4', '1.20.3': '1.20.3', '1.20.2': '1.20.2',
                              '1.20.1': '1.20.1', '1.20': '1.20', '1.19.x': '1.19.x', '1.19.4': '1.19.4', '1.19.3': '1.19.3',
                              '1.19.2': '1.19.2', '1.19.1': '1.19.1', '1.19': '1.19', '1.18.x': '1.18.x', '1.18.2': '1.18.2',
                              '1.18.1': '1.18.1', '1.18': '1.18', '1.17.x': '1.17.x', '1.17.1': '1.17.1', '1.17': '1.17',
                              '1.16.x': '1.16.x', '1.16.5': '1.16.5', '1.16.4': '1.16.4', '1.16.3': '1.16.3', '1.16.2': '1.16.2',
                              '1.16.1': '1.16.1', '1.16': '1.16', '1.15.x': '1.15.x', '1.15.2': '1.15.2', '1.15.1': '1.15.1',
                              '1.15': '1.15', '1.14.x': '1.14.x', '1.14.4': '1.14.4', '1.14.3': '1.14.3', '1.14.2': '1.14.2',
                              '1.14.1': '1.14.1', '1.14': '1.14', '1.13.x': '1.13.x', '1.13.2': '1.13.2', '1.13.1': '1.13.1',
                              '1.13': '1.13', '1.12.x': '1.12.x', '1.12.2': '1.12.2', '1.12.1': '1.12.1', '1.12': '1.12',
                              '1.11.x': '1.11.x', '1.11.2': '1.11.2', '1.11.1': '1.11.1', '1.11': '1.11', '1.10.x': '1.10.x',
                              '1.10.2': '1.10.2', '1.10.1': '1.10.1', '1.10': '1.10', '1.9.x': '1.9.x', '1.9.4': '1.9.4',
                              '1.9': '1.9', '1.8.x': '1.8.x', '1.8.9': '1.8.9', '1.8.8': '1.8.8', '1.8': '1.8',
                              '1.7.x': '1.7.x', '1.7.10': '1.7.10', '1.7.9': '1.7.9', '1.7.8': '1.7.8', '1.7.5': '1.7.5',
                              '1.7.4': '1.7.4', '1.7.2': '1.7.2', '1.6.x': '1.6.x', '1.6.4': '1.6.4', '1.6.2': '1.6.2',
                              '1.5.2': '1.5.2', '1.4.x': '1.4.x', '1.4.7': '1.4.7', '1.4.3': '1.4.3', '1.4.2': '1.4.2',
                              '1.3.2': '1.3.2', '1.2.5': '1.2.5'}

        self.categories: dict = {'mod': {'_all_': None,
                                         '科技': 1, '魔法': 2, '冒险': 3, '农业': 4,
                                         '装饰': 5, 'LIB': 7, '安全': 6, '资源': 8,
                                         '世界': 9, '群系': 10, '生物': 11, '能源': 12,
                                         '存储': 13, '物流': 14, '道具': 15, '红石': 16,
                                         '食物': 17, '模型': 18, '指南': 19, '破坏': 20,
                                         '魔改': 21, 'Meme': 22, '实用': 23, '辅助': 24,
                                         '中式': 25, '日式': 26, '西式': 27, '恐怖': 28,
                                         '建材': 29, '生存': 30, '指令': 31, '优化': 32,
                                         '国创': 33, '关卡': 34, '结构': 35},
                                 'modpack': {'_all_': None,
                                             '科技': 1, '魔法': 2, '冒险': 3, '建筑': 4,
                                             '地图': 5, '任务': 6, '硬核': 7, '休闲': 8,
                                             '大型': 9, '轻量': 10, '剧情': 11, '水槽': 12,
                                             '空岛': 13, 'PvP': 14, '国创': 15}}

        self.loaders: dict = {'mod': {'_all_': None,
                                      'forge':1,
                                      'fabric':2,
                                      'rift':3,
                                      'liteloader':4,
                                      '数据包':5,
                                      '命令方块':6,
                                      '文件覆盖':7,
                                      '行为包':8,
                                      'quilt':11,
                                      'neoforge':13},
                              'modpack': {'_all_': None,
                                          'forge':1,
                                          'fabric':2,
                                          'quilt':3,
                                          '数据包':4,
                                          'liteloader':5,
                                          'rift':6,
                                          'neoforge':7}}

        self.side_types: dict = {'mod': {'_all_': None,
                                         '仅客户端': 1,
                                         '仅服务端': 2,
                                         '主客户端': 3,
                                         '主服务端': 4,
                                         '皆需安装': 5}}

        self.query_types: dict = {'mod': {'精准搜索': None,
                                          '模糊搜索': 'ngram'}}

    def Explore(self, *,
                      project_type: str = '', # 项目类型
                      page: int = 1, # 页数
                      limit: int = 10, # 返回数量限制
                      offset: int = 0, # 偏移量
                      version: str = '', # 游戏版本
                      category: str = '', # 分类
                      sort: str = '', # 排序方式
                      **addtional: dict):

        URL: str = f'https://www.mcmod.cn/'
        params: dict = {}

        # 设置搜索类型 | 默认为搜索Mod
        project_type = project_type if project_type in self.project_types else 'mod'
        URL = URL + self.project_types[project_type] + '.html'
        if project_type == 'mod': params['platform'] = 1 # JAVA Edition

        # 设置页索引
        if page > 0:
            params['page'] = page
        # 设置排序方式
        if sort in self.sort_types:
            params['sort'] = self.sort_types[sort]
        # 设置游戏版本
        if version in self.versions:
            params['mcver'] = self.versions[version]
        # 设置搜索的项目分类
        if category in self.categories[project_type]:
            params['category'] = self.categories[project_type][category]

        # 设置加载器(仅在搜索类型为'mod'时生效)
        if 'loader' in addtional and addtional['loader'] in self.loaders[project_type]:
            params['api'] = self.loaders[project_type][addtional['loader']]
        if 'side_type' in addtional and addtional['side_type'] in self.side_types[project_type]:
            params['mode'] = self.side_types[project_type][addtional['side_type']]
        if 'query_type' in addtional and addtional['query_type'] in self.query_types and project_type == 'mod':
            params['nlp'] = self.query_types[addtional['query_type']]

        for Key in list(params.keys()):
            if params[Key] is None: params.pop(Key)

        try:
            zResponse: _Response_ = _requests_get_(url=URL, params=params); zResponse.raise_for_status()
        except Exception as E: return []

        ProjectElements: list[_HTMLElement_] = _FormatHTML_(zResponse.text).SubElements('*//div[@class="modlist-list-frame"]//div[@class="modlist-block"]')
        Projects: list[dict] = []

        for ProjectElement in ProjectElements:
            URL: str = 'https://www.mcmod.cn' + ProjectElement.SubElement('./div[@class="title"]/p[@class="name"]/a[@target="_blank"]').Get('href')
            Name: str = ProjectElement.SubElement('./div[@class="title"]/p[@class="ename"]/a[@target="_blank"]').Text
            Name_CN: str = ProjectElement.SubElement('./div[@class="title"]/p[@class="name"]/a[@target="_blank"]').Text
            ID: str = _re_search_(rf'(\d+)\.html', URL.split('/')[-1])[1]

            URL_Icon: str = 'https:' + ProjectElement.SubElement('./div[@class="cover"]/a[@target="_blank"]/img').Get('src')
            Description: str = ProjectElement.SubElement('./div[@class="intro"]/a/span').Text
            Author: str = ''
            Categories: str = ''
            Downloads: str = ''
            Likes: str = ''
            ModifiedDate: str = ''
            Versions: str = ''
            Environment: str = ''

            Projects.append({
                'URL': URL,
                'Name': Name,
                'Name_CN': Name_CN,
                'ID': ID,
                
                'URL_Icon': URL_Icon,
                'Description': Description,
                'Author': Author,
                'Categories': Categories,
                'Downloads': Downloads,
                'Likes': Likes,
                'ModifiedDate': ModifiedDate,
                'Versions': Versions,
                'Environment': Environment
            })
        return Projects

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
        
        URL: str = f'https://www.mcmod.cn/'
        params: dict = {}

        # 设置搜索类型 | 默认为搜索Mod
        project_type = project_type if project_type in self.project_types else 'mod'
        URL = URL + self.project_types[project_type] + '.html'
        if project_type == 'mod': params['platform'] = 1 # JAVA Edition

        # 设置搜索条件
        if query and project_type == 'mod':
            params['key'] = query
        # 设置页索引
        if page > 0:
            params['page'] = page
        # 设置排序方式
        if sort in self.sort_types:
            params['sort'] = self.sort_types[sort]
        # 设置游戏版本
        if version in self.versions:
            params['mcver'] = self.versions[version]
        # 设置搜索的项目分类
        if category in self.categories[project_type]:
            params['category'] = self.categories[project_type][category]

        # 设置加载器(仅在搜索类型为'mod'时生效)
        if 'loader' in addtional and addtional['loader'] in self.loaders[project_type]:
            params['api'] = self.loaders[project_type][addtional['loader']]
        if 'side_type' in addtional and addtional['side_type'] in self.side_types[project_type]:
            params['mode'] = self.side_types[project_type][addtional['side_type']]
        if 'query_type' in addtional and addtional['query_type'] in self.query_types and project_type == 'mod':
            params['nlp'] = self.query_types[addtional['query_type']]

        for Key in list(params.keys()):
            if params[Key] is None or params[Key] == '': params.pop(Key)

        try:
            zResponse: _Response_ = _requests_get_(url=URL, params=params); zResponse.raise_for_status()
        except Exception as E: return []

        ProjectElements: list[_HTMLElement_] = _FormatHTML_(zResponse.text).SubElements('*//div[@class="modlist-list-frame"]//div[@class="modlist-block"]')
        Projects: list[dict] = []

        for ProjectElement in ProjectElements:
            URL: str = 'https://www.mcmod.cn' + ProjectElement.SubElement('./div[@class="title"]/p[@class="name"]/a[@target="_blank"]').Get('href')
            Name: str = ProjectElement.SubElement('./div[@class="title"]/p[@class="ename"]/a[@target="_blank"]').Text
            Name_CN: str = ProjectElement.SubElement('./div[@class="title"]/p[@class="name"]/a[@target="_blank"]').Text
            ID: str = _re_search_(rf'(\d+)\.html', URL.split('/')[-1])[1]

            URL_Icon: str = 'https:' + ProjectElement.SubElement('./div[@class="cover"]/a[@target="_blank"]/img').Get('src')
            Description: str = ProjectElement.SubElement('./div[@class="intro"]/a/span').Text
            Author: str = ''
            Categories: str = ''
            Downloads: str = ''
            Likes: str = ''
            ModifiedDate: str = ''
            Versions: str = ''
            Environment: str = ''

            Projects.append({
                'URL': URL,
                'Name': Name,
                'Name_CN': Name_CN,
                'ID': ID,
                
                'URL_Icon': URL_Icon,
                'Description': Description,
                'Author': Author,
                'Categories': Categories,
                'Downloads': Downloads,
                'Likes': Likes,
                'ModifiedDate': ModifiedDate,
                'Versions': Versions,
                'Environment': Environment
            })
        return Projects

    def Project(self, URL: str) -> dict:
        pass

    def Locate(self, URL: str) -> list[dict]:
        return [{}]

def GetInterface() -> Interface:
    return Interface()