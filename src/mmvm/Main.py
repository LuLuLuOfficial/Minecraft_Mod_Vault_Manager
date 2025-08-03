from fastapi import FastAPI, Query, Request

from Plugins.Interface_BASIC import Interface
from Plugins.Interface_MODRINTH import GetInterface as GetInterface_MODRINTH
from Plugins.Interface_CURSEFORGE import GetInterface as GetInterface_CURSEFORGE
from Plugins.Interface_MCMOD import GetInterface as GetInterface_MCMOD

from pprint import pprint

Interface_MODRINTH: Interface = GetInterface_MODRINTH()
Interface_MCMOD: Interface = GetInterface_MCMOD()
Interface_CURSEFORGE: Interface = GetInterface_CURSEFORGE()

# 创建FastAPI实例
app = FastAPI(
    title="Minecraft Mod Vault Manager",
    # description="一个简单的用户管理API示例",
    # version="1.0.0"
)

@app.get("/")
async def root():
    return 'Minecraft Mod Vault Manager'

@app.get("/Explore")
async def Explore(
    engine: str,
    addtional: Request,
    project_type: str = Query(''),
    page: int = Query(1),
    limit: int = Query(10),
    offset: int = Query(0),
    version: str = Query(''),
    category: str = Query(''),
    sort: str = Query('')
) -> list[dict]:
    match engine:
        case 'MCMod':
            zInterface: Interface = Interface_MCMOD
        case 'Modrinth':
            zInterface: Interface = Interface_MODRINTH
        case 'CurseForge':
            zInterface: Interface = Interface_CURSEFORGE
        case _: return []

    kwargs: dict = {
        "project_type": project_type,
        "page": page,
        "limit": limit,
        "offset": offset,
        "version": version,
        "category": category,
        "sort": sort
    }
    addtional: dict = {Key: Value for Key, Value in dict(addtional.query_params).items() if Key not in kwargs and Key != 'engine'}

    return zInterface.Explore(
        project_type=project_type,
        page=page,
        limit=limit,
        offset=offset,
        version=version,
        category=category,
        sort=sort,
        **addtional
    )

@app.get('/Search')
async def Search(
    engine: str,
    addtional: Request,
    query: str = Query(''),
    project_type: str = Query(''),
    page: int = Query(1),
    limit: int = Query(10),
    offset: int = Query(0),
    version: str = Query(''),
    category: str = Query(''),
    sort: str = Query('')
) -> list[dict]:
    match engine:
        case 'MCMod':
            zInterface: Interface = Interface_MCMOD
        case 'Modrinth':
            zInterface: Interface = Interface_MODRINTH
        case 'CurseForge':
            zInterface: Interface = Interface_CURSEFORGE
        case _: return []

    kwargs: dict = {
        "query": query,
        "project_type": project_type,
        "page": page,
        "limit": limit,
        "offset": offset,
        "version": version,
        "category": category,
        "sort": sort
    }
    addtional: dict = {Key: Value for Key, Value in dict(addtional.query_params).items() if Key not in kwargs and Key != 'engine'}

    return zInterface.Search(
        query=query,
        project_type=project_type,
        page=page,
        limit=limit,
        offset=offset,
        version=version,
        category=category,
        sort=sort,
        **addtional
    )

@app.post('/Project')
async def Project(
    engine: str,
    addtional: Request,
    project_info: dict
):
    match engine:
        case 'MCMod':
            zInterface: Interface = Interface_MCMOD
        case 'Modrinth':
            zInterface: Interface = Interface_MODRINTH
        case 'CurseForge':
            zInterface: Interface = Interface_CURSEFORGE
        case _: return []

    addtional: dict = {Key: Value for Key, Value in dict(addtional.query_params).items() if Key != 'project_info' and Key != 'engine'}

    return zInterface.Project(
        project_info,
        **addtional
    )

@app.post('/Locate')
async def Locate(
    engine: str,
    addtional: Request,
    project_info: dict,
    versions: str = Query('')
):
    match engine:
        case 'MCMod':
            zInterface: Interface = Interface_MCMOD
        case 'Modrinth':
            zInterface: Interface = Interface_MODRINTH
        case 'CurseForge':
            zInterface: Interface = Interface_CURSEFORGE
        case _: return []

    addtional: dict = {Key: Value for Key, Value in dict(addtional.query_params).items() if Key != 'project_info' and Key != 'engine' and Key != 'versions'}

    return zInterface.Locate(
        project_info,
        versions=versions,
        **addtional
    )
