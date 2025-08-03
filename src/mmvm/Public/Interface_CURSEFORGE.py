from mmvm.Public.LogManager import LogManager

from Plugins.Interface_BASIC import Interface
from Plugins.Interface_CURSEFORGE import GetInterface as GetInterface_CURSEFORGE

Interface_CURSEFORGE: Interface = GetInterface_CURSEFORGE()

LogManager('Interface_CURSEFORGE Initialize Succeed')