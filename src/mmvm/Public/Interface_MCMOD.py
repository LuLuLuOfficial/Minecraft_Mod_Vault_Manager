from mmvm.Public.LogManager import LogManager

from Plugins.Interface_BASIC import Interface
from Plugins.Interface_MCMOD import GetInterface as GetInterface_MCMOD

Interface_MCMOD: Interface = GetInterface_MCMOD()

LogManager('Interface_MCMOD Initialize Succeed')