from zipfile import ZipFile
from json import load

def func1():
    jar_path, json_path = r'files\anvilcraft-fabric-1.20.1-1.4.1+pre-release.2.jar', 'fabric.mod.json'
    with ZipFile(jar_path, 'r') as jar:
        with jar.open(json_path) as file:
            return load(file)["depends"]

print(func1())