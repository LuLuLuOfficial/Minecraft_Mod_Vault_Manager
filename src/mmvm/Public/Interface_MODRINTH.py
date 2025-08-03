from mmvm.Public.LogManager import LogManager

from Plugins.Interface_BASIC import Interface
from Plugins.Interface_MODRINTH import GetInterface as GetInterface_MODRINTH

Interface_MODRINTH: Interface = GetInterface_MODRINTH()

LogManager('Interface_MODRINTH Initialize Succeed')