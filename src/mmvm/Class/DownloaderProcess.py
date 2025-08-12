from multiprocessing import Process, Pipe
from multiprocessing import Lock as GetLock, Value
from multiprocessing.synchronize import Lock
from os import getpid
from time import sleep

from mmvm.Class.DownloaderThreadPool import DownloaderThreadPool
from mmvm.Public.LogManager import LogManager

class DownloaderProcess(Process):
    def __init__(self,
                 Name: str,
                 NumPools: int = 3,
                 PoolSize: int = 2,
                 QueueSize: int = 5,
                 ReTryTimes: int = 3):
        super().__init__()
        self.name = "DownloaderProcess"
        self.daemon = True
        self.Args: dict = {
            'Name': Name,
            'NumPools': NumPools,
            'PoolSize': PoolSize,
            'QueueSize': QueueSize,
            'ReTryTimes': ReTryTimes
        }

        self.ProcessPID = Value('i', 0)
        self.Tasks_Last: list = []
        self.TaskSender, self.TaskGeter = Pipe()
        self.TaskAsker, self.TaskAnswer = Pipe()
        self.SDController, self.SDExecutor = Pipe()

    def AddTask(self, Task: dict):
        if self.TaskSender.poll() and self.TaskSender.recv() == 'TaskWaiting':
            self.TaskSender.send(Task)
            return True
        else:
            return False

    def GetTaskProgress(self):
        self.TaskAsker.send('TaskReturnPls')
        if self.TaskAsker.poll():
            Tasks: list = self.TaskAsker.recv()
            if Tasks: self.Tasks_Last = Tasks
        return self.Tasks_Last

    def Shutdown(self):
        LogManager("下载器: 专用进程接受关闭信号, 开始尝试结束下载器")
        self.SDController.send('Shutdown')
        LogManager("下载器: DownloaderThreadPool 线程池结束信号已发送")
        for Index in range(15):
            if self.SDController.poll() and self.SDController.recv() == 'TryShutdown':
                LogManager("下载器: DownloaderThreadPool 线程池结束指令已被 DownloaderProcess 进程工作循环接收并执行, 开始等待 DownloaderThreadPool 线程结束")
                break
            else:
                sleep(1.0)
        else:
            LogManager("下载器: DownloaderThreadPool 线程池结束指令无法被 DownloaderProcess 进程工作循环接收并执行, 尝试结束下载器失败")
            return None
        self.join()
        if self.SDController.poll(1): return self.SDController.recv()

    def GetPID(self) -> int | None:
        with self.ProcessPID.get_lock():
            return self.ProcessPID.value or None

    def run(self):
        with self.ProcessPID.get_lock(): self.ProcessPID.value = getpid()
        self.Tasks: list[dict] = []
        self.TasksLock: Lock = GetLock()
        self.zDownloader: DownloaderThreadPool = DownloaderThreadPool(**self.Args)
        
        LogManager("下载器: 专用进程 DownloaderProcess 初始化完成, 工作循环成功启动")
        while True:
            if self.TaskGeter.poll():
                with self.TasksLock:
                    self.Tasks.append(self.TaskGeter.recv())
                self.zDownloader.AddTask(self.Tasks[-1])
            else:
                self.TaskGeter.send('TaskWaiting')

            if self.TaskAnswer.poll(0.1) and self.TaskAnswer.recv() == 'TaskReturnPls':
                self.TaskAnswer.send([{
                    'name': Task['name'],
                    'url': Task['url'],
                    'path': Task['path'],
                    'file': Task['file'],
                    'size': Task['size'],
                    'hash': {
                        'hash_type': Task['hash']['hash_type'],
                        'hash_value': Task['hash']['hash_value']
                    },
                    'progress': Task['progress'],
                    'status': Task['status'],
                    'timestamp': {
                        'start': Task['timestamp']['start'],
                        'end': Task['timestamp']['end'],
                    }
                } for Task in self.Tasks])

            if self.SDExecutor.poll() and self.SDExecutor.recv() == 'Shutdown':
                self.SDExecutor.send('TryShutdown')
                self.SDExecutor.send(self.zDownloader.Shutdown())
                self.zDownloader.MasterThread.join()
                self.TaskAnswer.send([{
                    'name': Task['name'],
                    'url': Task['url'],
                    'file': Task['file'],
                    'size': Task['size'],
                    'hash': {
                        'hash_type': Task['hash']['hash_type'],
                        'hash_value': Task['hash']['hash_value']
                    },
                    'progress': Task['progress'],
                    'status': Task['status'],
                    'timestamp': {
                        'start': Task['timestamp']['start'],
                        'end': Task['timestamp']['end'],
                    }
                } for Task in self.Tasks])
                break
        LogManager("下载器: DownloaderProcess 工作循环结束, DownloaderProcess 进程将被退出")

def GetDownloader(Name: str,
                  NumPools: int = 3,
                  PoolSize: int = 2,
                  QueueSize: int = 5,
                  ReTryTimes: int = 3) -> DownloaderProcess:
    zDownloader = DownloaderProcess(
        Name=Name,
        NumPools=NumPools,
        PoolSize=PoolSize,
        QueueSize=QueueSize,
        ReTryTimes=ReTryTimes
    )
    zDownloader.start()
    while zDownloader.GetPID() is None: sleep(0.1)
    return zDownloader

if __name__ == '__main__':
    from pprint import pprint
    # 测试任务
    Tasks = [{
        'name': 'test_download_1',
        'url': 'https://www.wireshark.org/download/win64/all-versions/Wireshark-4.4.8-x64.exe',
        'path': 'files',
        'file': 'files/WiresharkPortable64_4.4.8.paf.exe',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }]

    zDownloader = GetDownloader(
        Name="TestDownloader",
        NumPools=3,
        PoolSize=2,
        QueueSize=5
    )
    print(zDownloader.GetPID())

    # 添加任务
    Index: int = 0
    ReTryTimes: int = 3
    ReTryed: int = 0
    while Index < len(Tasks):
        State: bool = zDownloader.AddTask(Tasks[Index])
        if State:
            # print(f"任务添加成功: {Tasks[Index]['name']}")
            Index += 1
            ReTryed = 0
        elif ReTryed < ReTryTimes:
            # print(f"任务添加失败: {Tasks[Index]['name']}, 将在 1 秒后重试")
            ReTryed += 1

    Index = 30
    while 1 and Index:
        Index -= 1
        sleep(1)
        # pprint(zTasks)
        States = [Task['status'] == 'Completed' or Task['status'] == 'Failed' for Task in zDownloader.GetTaskProgress()]
        Finished = all(States)
        print(Finished, States)
        if Finished and States: break

    ShutdownResult: list | None = None
    while ShutdownResult == None:
        ShutdownResult = zDownloader.Shutdown()
        sleep(1)
        print('结束失败')
    pprint(ShutdownResult)

