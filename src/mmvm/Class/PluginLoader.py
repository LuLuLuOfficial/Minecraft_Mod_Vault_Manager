from pylucas.fileops import ListFiles
from importlib.util import spec_from_file_location, module_from_spec
from types import ModuleType
from importlib.machinery import ModuleSpec
from mmvm.Public.Instances import LogManager
from mmvm.Class.ModuleInterface import ModuleInterface, Interface
from typing import Literal

class Loader():
    def __init__(self):
        self.Root: str = 'Plugins'
        self.Modules_Interface: dict[str, ModuleInterface] = {FileName.replace('.py', ''): None for FileName in ListFiles(Root=f'{self.Root}\\Interface', Types='*.py', Includes='Interface', Mode='Name')}

        self.GetModules_Interface()

    def __call__(self, Type: Literal['Modules_Interface'], ModuleName: str):
        match Type:
            case 'Modules_Interface':
                return self.Modules_Interface[ModuleName]['Interface']

    def GetModules_Interface(self) -> None:
        RequiredAttrs_Module: set = {'version', 'name', 'author', 'Interface', 'GetInterface'}
        RequiredAttrs_Class_Interface: set = {'Explore', 'Search', 'Locate'}
        for ModuleName in list(self.Modules_Interface.keys()):
            # 创建模块规范
            Spec: ModuleSpec = spec_from_file_location(ModuleName, f'{self.Root}\\Interface\\{ModuleName}.py')
            # 创建空模块对象
            Module: ModuleType = module_from_spec(Spec)
            # 将模块加载至模块对象
            Spec.loader.exec_module(Module); Module: ModuleInterface

            if not RequiredAttrs_Module.issubset({Attr for Attr in dir(Module) if not Attr.startswith('_')}):
                LogManager(f'Module <{ModuleName}> is not a valid module'); continue
            
            if not RequiredAttrs_Class_Interface.issubset({Attr for Attr in dir(Module.Interface) if not Attr.startswith('_')}):
                LogManager(f'Class Interface in Module <{ModuleName}> is not up to code'); continue

            # 将模块对象添加至模块字典
            self.Modules_Interface[ModuleName] = {'version': Module.version,
                                                  'name': Module.name,
                                                  'author': Module.author,
                                                  'Interface': Module.GetInterface()}

if __name__ == "__main__":
    from pprint import pprint
    Test = Loader()
    zInterface: Interface = Test(Type='Modules_Interface', ModuleName='Interface_MODRINTH')
    pprint(zInterface.Explore(limit=1))

    zInterface: Interface = Test(Type='Modules_Interface', ModuleName='Interface_MCMOD')
    pprint(zInterface.Explore())
