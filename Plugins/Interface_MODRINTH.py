from requests import get as _requests_get_
from requests.models import Response as _Response_
from aiohttp import ClientSession as _ClientSession_
from asyncio import gather as _asyncio_gather_
from asyncio import run as _asyncio_run_
from Plugins.Interface_BASIC import Interface as Interface_Basic

APIs: dict[str, str] = {
    'GetProjectType': 'https://api.modrinth.com/v2/tag/project_type',
    'GetGameVersions': 'https://api.modrinth.com/v2/tag/game_version',
    'GetCategories': 'https://api.modrinth.com/v2/tag/category',
    'GetLoaders': 'https://api.modrinth.com/v2/tag/loader',
    'GetSideTypes': 'https://api.modrinth.com/v2/tag/side_type',
}

async def GetProjectType(Session: _ClientSession_) -> dict:
    try:
        async with Session.get(APIs['GetProjectType']) as zResponse:
            zResponse.raise_for_status()
            ProjectTypes: dict = {ProjectType: ProjectType for ProjectType in await zResponse.json()}
            ProjectTypes['_all_'] = None
            return ProjectTypes
    except:
        return {}

async def GetSortTypes(Session: _ClientSession_) -> dict:
    return {
        '_default_': None,
        'relevance': 'relevance',
        'downloads': 'downloads',
        'follows': 'follows',
        'newest': 'newest',
        'updated': 'updated'
    }

async def GetGameVersions(Session: _ClientSession_) -> dict:
    try:
        async with Session.get(APIs['GetGameVersions']) as zResponse:
            zResponse.raise_for_status()
            GameVersions: dict = {GameVersion['version']: GameVersion['version'] for GameVersion in await zResponse.json() if GameVersion['version_type'] == 'release'}
            GameVersions['_all_'] = None
            return GameVersions
    except:
        return {}

async def GetCategories(Session: _ClientSession_) -> dict:
    try:
        # 获取 project_types
        async with Session.get(APIs['GetProjectType']) as zResponse:
            zResponse.raise_for_status()
            ProjectTypes = await zResponse.json()

        # 获取 categories
        async with Session.get(APIs['GetCategories']) as zResponse:
            zResponse.raise_for_status()
            Categories: dict[str, dict] = {ProjectType: {} for ProjectType in ProjectTypes}
            CategoriesInfo = await zResponse.json()

        for Category in CategoriesInfo:
            Categories[Category['project_type']].update({Category['name']: Category['name']})

        Categories['plugin'] = Categories['mod']; Categories['datapack'] = Categories['mod']
        for ProjectType in ProjectTypes: Categories[ProjectType].update({'_all_': None})

    except: pass
    else: return Categories
    return dict()

async def GetLoaders(Session: _ClientSession_) -> dict:
    try:
        async with Session.get(APIs['GetLoaders']) as zResponse:
            zResponse.raise_for_status()
            LoadersInfo = await zResponse.json()

        async with Session.get(APIs['GetProjectType']) as zResponse:
            zResponse.raise_for_status()
            ProjectTypes = await zResponse.json()

        Loaders: dict[str, dict] = {ProjectType: {} for ProjectType in ProjectTypes}

        for LoaderInfo in LoadersInfo:
            for ProjectType in ProjectTypes:
                if ProjectType in LoaderInfo['supported_project_types']:
                    Loaders[ProjectType].update({LoaderInfo['name']: LoaderInfo['name']})

        for ProjectType in ProjectTypes:
            Loaders[ProjectType].update({'_all_': None})

    except: pass
    else: return Loaders
    return dict()

async def GetSideTypes(Session: _ClientSession_) -> dict:
    try:
        async with Session.get(APIs['GetSideTypes']) as zResponse:
            zResponse.raise_for_status()
            SideTypes: dict = {'Client': await zResponse.json(), 'Server': await zResponse.json()}
        SideTypes.update({'_all_': None})
    except: pass
    else: return SideTypes
    return {}

class Interface(Interface_Basic): # 根据 Interface_MCMOD 的规范写一下
    def __init__(self):
        self.project_types: dict = None

        self.sort_types: dict = None

        self.versions: dict = None

        self.categories: dict = None

        self.loaders: dict = None

        self.side_types: dict = None

        self.query_types: dict = None

    async def async_init(self):
        """异步初始化方法，用于获取所有数据并赋值"""
        async with _ClientSession_() as session:
            # 并发获取所有数据（可选，也可顺序执行）
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
        return self  # 支持链式调用

    @property
    def name(self) -> str:
        return 'Interface_MODRINTH'
    
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
        return 'MODRINTH接口'

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
        URL: str = 'https://api.modrinth.com/v2/search'
        params: dict = {
            'facets': {
                'project_type': [],
                'categories': [],
                'versions': [],
                'client_side': [],
                'server_side': [],
                'open_source': []
            }
        }

        project_type = project_type if project_type in self.project_types else 'mod'

        if sort in self.sort_types:
            params['index'] = sort
        if offset > 0:
            params['offset'] = offset
        if limit > 0:
            params['limit'] = limit

        if project_type in self.project_types:
            params['facets']['project_type'].append(project_type)
        if category in self.categories:
            params['facets']['categories'].append(category)
        if version in self.versions:
            params['facets']['versions'].append(version)

        if 'loader' in addtional and addtional['loader'] in self.loaders[project_type]:
            params['facets']['categories'].append(addtional['loader'])

        if 'client_side' in addtional and addtional['client_side'] in self.side_types['Client']:
            params['facets']['client_side'].append(addtional['client_side'])

        if 'server_side' in addtional and addtional['server_side'] in self.side_types['Server']:
            params['facets']['server_side'].append(addtional['server_side'])

        params['facets'] = '[' + ','.join([f'["{facet}:{facetinfo}"]' for facet in params['facets'] for facetinfo in params['facets'][facet] if params['facets'][facet]]) + ']'
        if params['facets'] == '[]': params.pop('facets')

        zResponse: _Response_ = _requests_get_(url=URL, params=params)

        try:
            zResponse: _Response_ = _requests_get_(url=URL, params=params); zResponse.raise_for_status()
        except Exception as E: return []

        Projects: list[dict] = []

        for Project in zResponse.json()['hits']:
            Name: str = Project['title']
            Name_CN: str = ''
            ID: str = Project['project_id']
            URL: str = f"https://modrinth.com/{Project['project_type']}/{Project['slug']}"

            URL_Icon: str = Project['icon_url']
            Description: str = Project['description']
            Author: str = Project['author']
            Categories: str = Project['categories']
            Downloads: str = Project['downloads']
            Likes: str = Project['follows']
            ModifiedDate: str = Project['date_modified']
            Versions: str = Project['versions']
            Environment: str = {'client_side': Project['client_side'],
                                'server_side': Project['server_side'],}

            Projects.append({
                'Name': Name,
                'Name_CN': Name_CN,
                'ID': ID,
                'URL': URL,
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
        URL: str = 'https://api.modrinth.com/v2/search'
        params: dict = {
            'facets': {
                'project_type': [],
                'categories': [],
                'versions': [],
                'client_side': [],
                'server_side': [],
                'open_source': []
            }
        }

        project_type = project_type if project_type in self.project_types else 'mod'

        if query:
            params['query'] = query
        if sort in self.sort_types:
            params['index'] = sort
        if offset > 0:
            params['offset'] = offset
        if limit > 0:
            params['limit'] = limit

        if project_type in self.project_types:
            params['facets']['project_type'].append(project_type)
        if category in self.categories:
            params['facets']['categories'].append(category)
        if version in self.versions:
            params['facets']['versions'].append(version)

        if 'loader' in addtional and addtional['loader'] in self.loaders[project_type]:
            params['facets']['categories'].append(addtional['loader'])

        if 'client_side' in addtional and addtional['client_side'] in self.side_types['Client']:
            params['facets']['client_side'].append(addtional['client_side'])

        if 'server_side' in addtional and addtional['server_side'] in self.side_types['Server']:
            params['facets']['server_side'].append(addtional['server_side'])

        params['facets'] = '[' + ','.join([f'["{facet}:{facetinfo}"]' for facet in params['facets'] for facetinfo in params['facets'][facet] if params['facets'][facet]]) + ']'
        if params['facets'] == '[]': params.pop('facets')

        try:
            zResponse: _Response_ = _requests_get_(url=URL, params=params); zResponse.raise_for_status()
        except Exception as E: return []

        Projects: list[dict] = []

        for Project in zResponse.json()['hits']:
            Name: str = Project['title']
            Name_CN: str = ''
            ID: str = Project['project_id']
            URL: str = f"https://modrinth.com/{Project['project_type']}/{Project['slug']}"

            URL_Icon: str = Project['icon_url']
            Description: str = Project['description']
            Author: str = Project['author']
            Categories: str = Project['categories']
            Downloads: str = Project['downloads']
            Likes: str = Project['follows']
            ModifiedDate: str = Project['date_modified']
            Versions: str = Project['versions']
            Environment: str = {'client_side': Project['client_side'],
                                'server_side': Project['server_side'],}

            Projects.append({
                'Name': Name,
                'Name_CN': Name_CN,
                'ID': ID,
                'ProjectType': project_type,
                'URL': URL,
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

    def Project(self, project_info: dict, # 项目信息 来源于 Explore 或 Search 的返回值
                      **addtional: dict) -> dict:
        ID: str = project_info['ID'] if 'ID' in project_info else ''
        Slug: str = project_info['Name'] if 'Name' in project_info else ''
        LocateKey: str = ID or Slug
        if not LocateKey: return {}

        URL: str = f'https://api.modrinth.com/v2/project/{ID or Slug}'

        try:
            zResponse: _Response_ = _requests_get_(url=URL)
            zResponse.raise_for_status()
            ProjectInfo: dict = zResponse.json()
        except: return {}

        ProjectInfo: dict = {
                'SpecialInfo': {
                    'WebSite':'Modrinth',
                    'ID': ProjectInfo['id']
                },

                'ID': ProjectInfo['slug'],
                'Name': ProjectInfo['title'],
                'Name_CN': '',
                'Description': ProjectInfo['description'],

                'Icon_URL': ProjectInfo['icon_url'],

                'SideType': {
                    "Client": ProjectInfo['client_side'],
                    "Server": ProjectInfo['server_side'],
                },
                'ProjectType': ProjectInfo['project_type'],
                'Loaders': ProjectInfo['loaders'],
                'GameVersions': ProjectInfo['game_versions'],
        }

        return ProjectInfo

    def Locate(self, project_info: dict, # 项目信息 来源于 Explore 或 Search 的返回值
                     versions: str | list[str] = '',
                     **addtional: dict) -> list[dict]:
        ID: str = project_info['ID'] if 'ID' in project_info else ''
        Slug: str = project_info['Name'] if 'Name' in project_info else ''
        LocateKey: str = ID or Slug

        if (not project_info['SpecialInfo']['WebSite'] == 'Modrinth' and
            not 'ProjectType' in project_info or
            not project_info['ProjectType'] in self.project_types and
            not LocateKey):
            return []

        URL: str = f'https://api.modrinth.com/v2/project/{ID or Slug}/version'
        params: dict[str, list] = {
            'loaders': [],
            'game_versions': []
        }

        for version in versions if isinstance(versions, list) else [versions]:
            if version in self.versions: params['game_versions'].append(f'\"{self.versions[version]}\"')

        if 'loaders' in addtional:
            for loader in addtional['loaders'] if isinstance(addtional['loaders'], list) else [addtional['loaders']]:
                params['loaders'].append(f'\"{loader}\"')

        for key in list(params): params[key] = '[' + ','.join(params[key]) + ']'

        try:
            zResponse: _Response_ = _requests_get_(url=URL, params=params)
            zResponse.raise_for_status()
            zProjectVersions: list[dict] = zResponse.json()
        except: return []

        ProjectVersions: list[dict] = []

        for ProjectVersion in zProjectVersions:
            ProjectVersions.append({
                'SpecialInfo': {
                    'WebSite':'Modrinth',
                    'ID': project_info['SpecialInfo']['ID']
                },

                'ID': project_info['ID'],
                'Name': project_info['Name'],
                'Name_CN': project_info['Name_CN'],
                'Description': project_info['Description'],

                'ProjectType': project_info['ProjectType'],
                'Dependency': {
                    'GameVersion': ProjectVersion['game_versions'],
                    'Loader': ProjectVersion['loaders'],
                    'Projects': [Project['project_id'] for Project in ProjectVersion['dependencies']]
                },
                'SideType':  project_info['SideType'],

                'Icon_URL': project_info['Icon_URL'],
                'Files': [{
                    'FileName': File['filename'],
                    'URL': File['url'],
                    'Hashes': File['hashes'],
                } for File in ProjectVersion['files']]
            })
        
        return ProjectVersions

def GetInterface():
    async def Initialize() -> Interface:
        zInterface = Interface()
        await zInterface.async_init()
        return zInterface
    return _asyncio_run_(Initialize())

if __name__ == "__main__":
    from pprint import pprint
    
    zInterface: Interface = GetInterface()

    # Explore
    print('='*50)
    pprint(zInterface.Explore(project_type='mod'))

    # Search
    print('='*50)
    pprint(zInterface.Search(query='carpet',
                             project_type='mod',
                             limit=1,
                             version='1.17.1',
                             loader='fabric'))
    
    # # Project
    # print('='*50)
    # project_info: dict = {'Author': 'altrisi','Categories': ['fabric', 'game-mechanics', 'utility'],'Description': 'Take full control over your vanilla game','Downloads': 2704425,'Environment': {'client_side': 'unsupported', 'server_side': 'required'},'ID': 'TQTTVgYE','Likes': 1793,'ModifiedDate': '2025-07-01T16:55:41.807912Z','Name': 'Carpet','Name_CN': '','ProjectType': 'mod','URL': 'https://modrinth.com/mod/carpet','URL_Icon': 'https://cdn.modrinth.com/data/TQTTVgYE/3ad650635d067b6bfa09403cf5e70e0947a05c07_96.webp','Versions': ['1.21.7']}
    # pprint(zInterface.Project(project_info=project_info))

    # Locate
    print('='*50)
    project_info: dict = {'SpecialInfo': {'WebSite': 'Modrinth', 'ID': 'TQTTVgYE'}, 'ID': 'carpet', 'Name': 'Carpet', 'Name_CN': '', 'Description': 'Take full control over your vanilla game', 'Icon_URL': 'https://cdn.modrinth.com/data/TQTTVgYE/3ad650635d067b6bfa09403cf5e70e0947a05c07_96.webp', 'SideType': {'Client': 'unsupported', 'Server': 'required'}, 'ProjectType': 'mod', 'Loaders': ['fabric'], 'GameVersions': ['1.21.7']}
    print(zInterface.Locate(project_info=project_info, versions='1.21.7', loaders='fabric'))