from json import load as json_load
from json import dump as json_dump
from datetime import datetime
from typing import Literal
from copy import deepcopy

from mmvm.Public.LogManager import LogManager
from Plugins.Interface_BASIC import Interface
from mmvm.Public.Interface_CURSEFORGE import Interface_CURSEFORGE
from mmvm.Public.Interface_MCMOD import Interface_MCMOD
from mmvm.Public.Interface_MODRINTH import Interface_MODRINTH

def GetBookmarks(Source: str,
                 Target: str = f'Data/FromBookmarks/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json') -> tuple[dict, str]:
    Bookmarks: dict = {}
    with open(file=Source, mode='r', encoding='utf-8') as File:
        Bookmarks = json_load(File)
        File.close()

    Bookmarks: list = Bookmarks['roots']['bookmark_bar']['children']
    for BookMarkGroup in Bookmarks:
        if BookMarkGroup['name'] == 'ModBookmarks':
            Bookmarks = BookMarkGroup['children']
            break
    else:
        raise Exception('No Bookmarks Group Found')

    zBookmarks: list = []
    for BookMarkGroup in Bookmarks:
        if BookMarkGroup['type'] == 'folder':
            zBookmarks += BookMarkGroup['children']

    Bookmarks: dict = {
        BookMark['name'][:-27] if BookMark['name'].endswith(' - MC百科|最大的Minecraft中文MOD百科') else BookMark['name']: BookMark['url']
        for BookMark in zBookmarks if not BookMark['url'].startswith('https://www.mcmod.cn/modlist.html')
        }

    with open(file=Target, mode='w', encoding='utf-8') as File:
        json_dump(Bookmarks, File, ensure_ascii=False, indent=4)
    
    return Bookmarks, Target

def LocateBookmarks(Engine: Literal['CurseForge', 'MCMod', 'Modrinth'],
                    BookmarksPath: str,
                    Bookmarks: dict[str, str] = {},
                    versions: str | list[str] = '',
                    **addtional: dict) -> dict:
    zInterface: Interface
    match Engine:
        case 'CurseForge': zInterface = Interface_CURSEFORGE
        case 'MCMod': zInterface = Interface_MCMOD
        case 'Modrinth': zInterface = Interface_MODRINTH
        case _: raise ValueError('Invalid Engine')
    
    if not isinstance(BookmarksPath, str): return
    if not Bookmarks:
        with open(BookmarksPath, 'r', encoding='utf-8') as File:
            Bookmarks: dict[str, str] = json_load(File)

    addtional_Locate: dict = deepcopy(addtional)
    if 'loader' in addtional_Locate: addtional_Locate['loaders'] = addtional_Locate.pop('loader')

    Locate_Succeed: dict = {}
    Locate_Failed: dict = {}

    for Key, Value in Bookmarks.items():
        LogManager(f'Now Trying to Locate: <{Key} | {Value}>')
        Name_CN = Key[:Key.rfind(' (')] if ' (' in Key and Key[-1] == ')' else Key
        ProjectInfo: dict = zInterface.Project(project_info={'URL': Value, 'Name_CN': Name_CN}, **addtional)
        ProjectInfo: list = zInterface.Locate(project_info=ProjectInfo, versions=versions, **addtional_Locate)
        if ProjectInfo:
            LogManager(f'Locate: ✅ <{Key}> Succeed')
            Locate_Succeed[Key] = ProjectInfo
        else:
            LogManager(f'Locate: ❌ <{Key}> Failed')
            Locate_Failed[Key] = Value

    with open(file=BookmarksPath, mode='w', encoding='utf-8') as File:
        json_dump(Locate_Succeed, File, ensure_ascii=False, indent=4)

    with open(file=BookmarksPath.replace('.json', 'Failed.json'), mode='w', encoding='utf-8') as File:
        json_dump(Locate_Failed, File, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    Bookmarks, BookmarksPath = GetBookmarks(Source=r"C:\Users\Lucas\AppData\Local\Google\Chrome\User Data\Default\Bookmarks")
    LocateBookmarks(Engine='MCMod', BookmarksPath=BookmarksPath, Bookmarks=Bookmarks, versions='1.20.1', loader='fabric')
