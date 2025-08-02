from pylucas.fileops import ListFiles
from importlib.util import spec_from_file_location, module_from_spec
from types import ModuleType
from importlib.machinery import ModuleSpec
from mmvm.Public.Instances import LogManager
from Plugins.Interface_Example import Interface_Basic as Interface
from typing import Literal

class PluginManager():
    def __init__(self):
        self.Root: str = 'Plugins'
        self.Plugins: dict[str, Interface] = {}

        self.DiscoverPlugins()

    def DiscoverPlugins(self):
        self.Plugins = {FileName.replace('.py', ''): None for FileName in ListFiles(Root=self.Root, Types='*.py', Mode='Name')}
        print(self.Plugins)

    def LoadPlugin(self) -> None:
        RequiredAttrs_Class: set = {'name', 'version', 'ptype', 'author', 'description', 'Explore', 'Search', 'Project', 'Locate'}
        for ModuleName in list(self.Modules.keys()):
            # 创建模块规范
            Spec: ModuleSpec = spec_from_file_location(ModuleName, f'{self.Root}\\Interface\\{ModuleName}.py')
            # 创建空模块对象
            Module: ModuleType = module_from_spec(Spec)
            # 将模块加载至模块对象
            Spec.loader.exec_module(Module); Module: Interface

            if not RequiredAttrs_Module.issubset({Attr for Attr in dir(Module) if not Attr.startswith('_')}):
                LogManager(f'Module <{ModuleName}> is not a valid module'); continue
            
            if not RequiredAttrs_Class_Interface.issubset({Attr for Attr in dir(Module.Interface) if not Attr.startswith('_')}):
                LogManager(f'Class Interface in Module <{ModuleName}> is not up to code'); continue

            # 将模块对象实例添加至模块字典
            self.Modules[ModuleName] = {'version': Module.version,
                                        'name': Module.name,
                                        'author': Module.author,
                                        'Instance': Module.GetInterface()}

if __name__ == "__main__":
    from pprint import pprint
    Test = PluginManager()
    # zInterface: Interface = Test(ModuleName='Interface_MODRINTH')

    # ProjectInfo: dict = {'SpecialInfo': {'WebSite': 'Modrinth', 'ID': 'TQTTVgYE'}, 'ID': 'carpet', 'Name': 'Carpet', 'Name_CN': '', 'Description': 'Take full control over your vanilla game', 'Icon_URL': 'https://cdn.modrinth.com/data/TQTTVgYE/3ad650635d067b6bfa09403cf5e70e0947a05c07_96.webp', 'SideType': {'Client': 'unsupported', 'Server': 'required'}, 'ProjectType': 'mod', 'Loaders': ['fabric'], 'GameVersions': ['1.14.4', '1.15', '1.15.1', '1.15.2', '1.16', '1.16.1', '1.16.2', '1.16.3', '1.16.4', '1.16.5', '1.17.1', '1.18', '1.18.1', '1.18.2', '1.19', '1.19.1', '1.19.2', '1.19.3', '23w03a', '23w04a', '23w05a', '23w06a', '1.19.4-pre1', '1.19.4-pre2', '1.19.4-pre3', '1.19.4-pre4', '1.19.4-rc1', '1.19.4-rc2', '1.19.4', '23w12a', '23w13a', '23w14a', '23w16a', '23w17a', '23w18a', '1.20-pre1', '1.20-pre2', '1.20-pre3', '1.20-pre4', '1.20-pre5', '1.20-pre6', '1.20-pre7', '1.20-rc1', '1.20', '1.20.1', '23w31a', '23w32a', '23w35a', '1.20.2-pre1', '1.20.2-pre2', '1.20.2-pre4', '1.20.2-rc1', '1.20.2', '23w40a', '23w42a', '23w43a', '23w43b', '23w44a', '23w45a', '23w46a', '1.20.3-pre1', '1.20.3-pre2', '1.20.3-pre3', '1.20.3', '1.20.4', '23w51b', '24w03a', '24w04a', '24w05a', '24w06a', '24w07a', '24w09a', '24w10a', '24w11a', '24w12a', '24w13a', '1.20.5-pre1', '1.20.5-pre2', '1.20.5', '1.20.6', '24w18a', '24w20a', '24w21a', '1.21-pre1', '1.21-pre3', '1.21', '1.21.1', '24w33a', '24w34a', '24w35a', '24w36a', '24w37a', '24w38a', '24w40a', '1.21.2-pre1', '1.21.2-pre2', '1.21.2-pre3', '1.21.2-pre4', '1.21.2-pre5', '1.21.2-rc1', '1.21.2', '1.21.3', '24w44a', '24w45a', '24w46a', '1.21.4-pre1', '1.21.4-pre2', '1.21.4-pre3', '1.21.4-rc1', '1.21.4', '25w02a', '25w03a', '25w04a', '25w05a', '25w06a', '25w07a', '25w08a', '25w09a', '25w09b', '25w10a', '1.21.5-pre1', '1.21.5', '25w15a', '25w16a', '25w17a', '25w18a', '25w19a', '25w20a', '25w21a', '1.21.6-pre1', '1.21.6', '1.21.7']}

    # pprint(zInterface.Locate(project_info=ProjectInfo, versions='1.21.7', loaders='fabric'))

