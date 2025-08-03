from os import makedirs as MakeDirs
from os.path import exists as FileExists
from os.path import join as PathJoin
from os import remove as RemoveFile

def CreateTestsPY(TargetDir: str, Range: int | range):
    if not FileExists(TargetDir):
        MakeDirs(TargetDir, exist_ok=True)
        print(f"指定的目录不存在, 已自动创建: {TargetDir}")

    if isinstance(Range, int): Range = range(1, Range+1)
    if not isinstance(Range, range): raise TypeError("参数Range必须是int或range类型")

    CreateCount: int = 0
    for FileIndex in Range:
        FilePath: str = PathJoin(TargetDir, f'Test_{FileIndex}.py')
        if FileExists(FilePath): continue
        with open(FilePath, 'w', encoding='utf-8') as File:
            File.close()
        CreateCount += 1
        print(f"已创建: {FilePath}")

    print(f"\n总共创建 {CreateCount} 个测试脚本.")

if __name__ == "__main__":
    CreateTestsPY(TargetDir='tests', Range=5)