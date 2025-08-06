from requests import get as requests_get
from requests import head as requests_head
from requests import Response
from os import makedirs as os_makedirs
from os.path import dirname as os_dirname
from threading import Lock, Thread
from queue import Queue, Empty as QueryEmptyError
from hashlib import new as NewHashingObj
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, Tuple
from time import time, sleep

from mmvm.Public.LogManager import LogManager

class DownloaderThreadPool():
    def __init__(self,
                 Name: str,
                 NumPools: int = 3,
                 PoolSize: int = 2,
                 QueueSize: int = 5,
                 ReTryTimes: int = 3):
        self.Name: str = Name
        self.NumPools: int = NumPools
        self.PoolSize: int = PoolSize
        self.ReTryTimes: int = ReTryTimes

        # 状态管理
        self.AliveLock: Lock = Lock()
        self.Alive: bool = True
        
        # 任务队列
        self.TaskQueue: Queue = Queue(maxsize=QueueSize)
        self.RemainingTasksLock: Lock = Lock()
        self.RemainingTasks: list = []
        
        # 执行器管理
        self.ExecutorsStateLock: Lock = Lock()
        self.ExecutorsState: list = [True for Index in range(self.NumPools)]  # True=空闲, False=忙碌
        self.Executors: list[ThreadPoolExecutor] = [
            ThreadPoolExecutor(
                max_workers=self.PoolSize,
                thread_name_prefix=f'{self.Name}_ThreadPool_{Index}',
            )
            for Index in range(self.NumPools)
        ]
        
        # 主工作线程
        self.MasterThread: Thread = Thread(
            target=self.WorkLoop,
            name=f'{self.Name}_MasterThread',
            daemon=True,
        )
        self.MasterThread.start()

    def WorkLoop(self):
        """主工作循环, 负责分派任务给空闲线程池"""
        LogManager("下载器: 线程池 DownloaderThreadPool 初始化完成, MasterThread 工作循环成功启动")
        while True:
            # 获取空闲线程池
            ExecutorIndex: int = self.FreeExecutorIndex()
            if ExecutorIndex == -1 or self.TaskQueue.empty():
                sleep(0.1)
            with self.AliveLock:
                sleep(0.1)
                if not self.Alive:
                    if self.TaskQueue.empty(): break
                    else:
                        LogManager("下载器: 尝试导出剩余待分派任务")
                        while not self.TaskQueue.empty():
                            try:
                                with self.RemainingTasksLock:
                                    self.RemainingTasks.append(self.TaskQueue.get_nowait())
                                    self.TaskQueue.task_done()
                            except QueryEmptyError:
                                break
                        with self.TaskQueue.all_tasks_done:
                            while self.TaskQueue.unfinished_tasks:
                                LogManager(f"下载器: 存在异常未结束任务, 尝试强制解除阻塞", 'Error')
                                self.TaskQueue.shutdown(immediate=True)
                        continue

                if ExecutorIndex == -1: continue

                # 获取任务
                try:
                    TaskName: str = 'UnknowTask'
                    TaskURL: str = 'UnknowURL'
                    FilePath: str = 'UnknowPath'

                    Task = self.TaskQueue.get(timeout=0.1)

                    self.ExecutorsState[ExecutorIndex] = False
                    
                    with Task['lock']:
                        TaskName = Task['name']
                        TaskURL = Task['url']
                        FilePath = Task['file']
                        Task['timestamp']['start'] = time()
                    
                    LogManager(f"任务 <{TaskName}> 报告: 分派至第 {ExecutorIndex} 线程池", 'Normal')

                    self.Executors[ExecutorIndex].submit(
                        self.ProcessTask,
                        Task,
                        TaskName,
                        TaskURL,
                        FilePath,
                        ExecutorIndex
                    )
                except QueryEmptyError:
                    # 没有任务时释放线程池
                    with self.ExecutorsStateLock:
                        self.ExecutorsState[ExecutorIndex] = True
                except Exception as E:
                    LogManager(f"任务 <{TaskName}> 异常: 分派至第 {ExecutorIndex} 线程池失败, 未预见的错误 [{type(E)}|{str(E)}], 任务已放弃", 'Error')
                    with self.ExecutorsStateLock:
                        self.ExecutorsState[ExecutorIndex] = True
                else:
                    self.TaskQueue.task_done()
        LogManager("下载器: MasterThread 工作循环结束, MasterThread 线程将被退出")

    def FreeExecutorIndex(self) -> int:
        """获取空闲线程池索引"""
        with self.ExecutorsStateLock:
            for Index, State in enumerate(self.ExecutorsState):
                if State:
                    self.ExecutorsState[Index] = False  # 标记为忙碌
                    return Index
        return -1

    def ProcessTask(self, Task: dict, TaskName: str, TaskURL: str, FilePath: str, ExecutorIndex: int):
        """处理单个下载任务"""
        try:
            # 准备任务（HEAD请求/创建目录等）
            ChunkedSupport, FileSize = self.PrepareTask(TaskName, TaskURL, FilePath)
            
            # 根据文件大小选择下载方式
            if ChunkedSupport and FileSize >= 1024 * 256:
                self.DownloadMultiThread(Task, TaskName, TaskURL, FilePath, ExecutorIndex, FileSize)
            else:
                self.DownloadSingleThread(Task, TaskName, TaskURL, FilePath, ExecutorIndex)

            # 哈希验证
            if not self.HashFile(Task): raise ValueError('Hash Validation Failed')
        except Exception as E:
            if isinstance(E, RuntimeError) and E.args[0] == 'cannot schedule new futures after shutdown':
                with Task['lock']:
                    Task['status'] = 'SendBack'
                LogManager(f"任务 <{TaskName}> 中止: 下载线程池已经关闭", 'Warn')
                self.RemainingTasks.append(Task)
            elif isinstance(E, ValueError) and E.args[0] == 'Hash Validation Failed':
                with Task['lock']:
                    Task['status'] = 'Failed'
                    LogManager(f"任务 <{TaskName}> 失败: 哈希校验未通过", 'Error')
            else:
                with Task['lock']:
                    Task['status'] = 'Failed'
                    LogManager(f"任务 <{TaskName}> 失败: 未预见的错误 [{type(E)}|{str(E)}]", 'Error')
        else:
            with Task['lock']:
                Task['timestamp']['end'] = time()
                Task['status'] = 'Completed'
                LogManager(f"任务 <{TaskName}> 完成: 下载成功", 'Normal')
        finally:
            # 释放线程池
            with self.ExecutorsStateLock:
                self.ExecutorsState[ExecutorIndex] = True

    def PrepareTask(self, TaskName: str, TaskURL: str, FilePath: str) -> Tuple[bool, int]:
        """准备任务: 执行HEAD请求, 创建目录等"""
        for Attempt in range(self.ReTryTimes):
            try:
                # 创建目录
                os_makedirs(os_dirname(FilePath), exist_ok=True)
                
                # 执行HEAD请求获取文件信息
                zResponse: Response = requests_head(TaskURL, allow_redirects=True, timeout=5)
                
                # 检查响应状态
                if zResponse.status_code != 200:
                    LogManager(f"任务 <{TaskName}> 异常: 连接文件服务器异常 <url|{TaskURL}> <StatusCode|{zResponse.status_code}>", 'Error')
                    return False, 0
                
                # 检查是否支持分块下载
                if zResponse.headers.get('accept-ranges') != 'bytes':
                    LogManager(f"任务 <{TaskName}> 报告: 不支持分块下载 <url|{TaskURL}>", 'Normal')
                    return False, 0
                else:
                    LogManager(f"任务 <{TaskName}> 报告: 支持分块下载 <url|{TaskURL}>", 'Normal')

                # 获取文件大小
                if not (ContentLength := zResponse.headers.get('content-length')):
                    LogManager(f"任务 <{TaskName}> 报告: 获取文件大小失败 <url|{TaskURL}>", 'Warn')
                    return False, 0
                
                return True, int(ContentLength)
            except Exception as E:
                LogManager(f"任务 <{TaskName}> 异常: 连接文件服务器失败, 未预见的错误 [{type(E)}|{str(E)}], 尝试次数[{Attempt+1}/{self.ReTryTimes})]", 'Error')
                sleep(1)
        else:
            return False, 0

    def DownloadMultiThread(self, Task: dict, TaskName: str, TaskURL: str, FilePath: str, ExecutorIndex: int, FileSize: int):
        """多线程下载实现"""
        # 预分配文件空间
        with open(FilePath, 'wb') as File:
            File.truncate(FileSize)
        
        # 计算分块
        ChunkSize = FileSize // self.PoolSize
        Futures = []
        
        # 提交分块下载任务
        for ChunkIndex in range(self.PoolSize):
            start = ChunkIndex * ChunkSize
            end = (FileSize - 1) if ChunkIndex == self.PoolSize - 1 else min(start + ChunkSize - 1, FileSize - 1)
            
            Futures.append(self.Executors[ExecutorIndex].submit(
                self.DownloadChunk,
                TaskName,
                TaskURL,
                FilePath,
                start,
                end,
                lambda growth: self.UpdateProgress(Task, growth)
            ))
        
        # 等待所有分块完成
        for Future in as_completed(Futures):
            if zException := Future.exception():
                raise zException

    def DownloadSingleThread(self, Task: dict, TaskName: str, TaskURL: str, FilePath: str, ExecutorIndex: int):
        """单线程下载实现"""
        Future = self.Executors[ExecutorIndex].submit(
            self.DownloadChunk,
            TaskName,
            TaskURL,
            FilePath,
            None,  # 无起始位置
            None,  # 无结束位置
            lambda growth: self.UpdateProgress(Task, growth)
        )

        # 等待任务完成
        if zException := Future.exception():
            raise zException

    def DownloadChunk(self, TaskName: str, TaskURL: str, FilePath: str, start: Optional[int], end: Optional[int], update_progress: Callable):
        """下载文件块"""
        headers: dict = {}
        if start is not None and end is not None:
            headers['Range'] = f'bytes={start}-{end}'
        
        try:
            zResponse: Response = requests_get(
                TaskURL,
                headers=headers,
                stream=True,
                timeout=10
                )
            zResponse.raise_for_status()

            mode = 'r+b' if start is not None else 'wb'
            with open(FilePath, mode) as f:
                if start is not None: f.seek(start)
                for Chunk in zResponse.iter_content(chunk_size=8192):
                    print(f'区块写入开始{time()}')
                    if Chunk:
                        f.write(Chunk)
                        update_progress(len(Chunk))
                    print(f'区块写入结束{time()}')
        except Exception as E:
            LogManager(f"任务 <{TaskName}> 异常: 下载失败, 未预见的错误: [{type(E)}|{str(E)}] <url|{TaskURL}>", 'Error')
            raise

    def UpdateProgress(self, Task: dict, growth: int):
        """线程安全的进度更新"""
        with Task['lock']:
            Task['progress'] += growth

    def HashFile(self, Task: dict) -> bool:
        """验证文件哈希"""
        TaskName: str = 'UnknowTask'
        FilePath: str = 'UnknowPath'
        HashValue: str = ''
        try:
            with Task['lock']:
                TaskName = Task['name']
                FilePath = Task['file']
                if not 'hash' in Task or 'hash_type' in Task['hash'] or 'hash_value' in Task['hash']:
                    raise KeyError('No HashInfo In Task Dict')
                HashValue = Task['hash']['hash_value']
                Hasher = NewHashingObj(Task['hash']['hash_type'].lower())

            with open(FilePath, 'rb') as f:
                for Chunk in iter(lambda: f.read(4096), b""):
                    Hasher.update(Chunk)

            return Hasher.hexdigest() == HashValue
        except KeyError:
            LogManager(f"任务 <{TaskName}> 报告: 任务中未包含哈希信息, 跳过目标文件哈希校验 <file_path|{FilePath}>", 'Warn')
            return True
        except FileNotFoundError:
            LogManager(f"任务 <{TaskName}> 异常: 无法进行哈希校验, 目标文件不存在 <file_path|{FilePath}>", 'Error')
            return False
        except Exception as E:
            LogManager(f"任务 <{TaskName}> 异常: 文件 <{FilePath}> 在哈希校验中出现未预见的错误 [{type(E)}|{str(E)}]", 'Error')
            return False

    def AddTask(self, Task: dict) -> bool:
        """添加下载任务"""
        # 为任务添加线程锁
        Task['lock'] = Lock()
        Task['status'] = 'Pending'
        Task['lock'] = Lock() 
        TaskName: str = 'UnknowTask'
        try:
            TaskName = Task['name']
            if self.TaskQueue.not_full:
                self.TaskQueue.put(Task)
                LogManager(f"任务 <{TaskName}> 报告: 任务成功添加至任务队列", 'Normal')
                return Task
            else:
                LogManager(f"任务 <{TaskName}> 报告: 任务队列已满", 'Warn')
                return Task
        except Exception as E:
            LogManager(f"任务 <{TaskName}> 报告: 无法添加任务至任务队列, 未预见的错误 [{type(E)}|{str(E)}]", 'Error')
            return Task

    def Shutdown(self) -> list:
        """关闭下载器"""
        # 停止接受新任务
        LogManager("下载器: 尝试结束任务分发循环")
        with self.AliveLock:
            self.Alive = False

        # 等待所有任务完成
        LogManager("下载器: 等待任务队列中已分派任务完成")
        self.TaskQueue.join()

        # 关闭所有线程池
        LogManager("下载器: 结束线程池 DownloaderThreadPool")
        for Executor in self.Executors:
            Executor.shutdown(wait=True)
        
        LogManager(f"下载器: 剩余未分派任务数 {len(self.RemainingTasks)}")

        LogManager("下载器: 线程池 DownloaderThreadPool 结束成功")

        return [{
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
        } for Task in self.RemainingTasks]

if __name__ == "__main__":
    from pprint import pprint
    # 测试任务
    Tasks = [{
        'name': 'test_download_1',
        'url': 'https://cdn.modrinth.com/data/SFQA3vF5/versions/nrqAIQFr/%21MoonlitPEM_2.1.3_FABRIC.jar',
        'path': 'files',
        'file': 'files/test1.jar',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }, {
        'name': 'test_download_2',
        'url': 'https://cdn.modrinth.com/data/SFQA3vF5/versions/nrqAIQFr/%21MoonlitPEM_2.1.3_FABRIC.jar',
        'path': 'files',
        'file': 'files/test2.jar',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }, {
        'name': 'test_download_3',
        'url': 'https://cdn.modrinth.com/data/SFQA3vF5/versions/nrqAIQFr/%21MoonlitPEM_2.1.3_FABRIC.jar',
        'path': 'files',
        'file': 'files/test3.jar',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }, {
        'name': 'test_download_4',
        'url': 'https://cdn.modrinth.com/data/SFQA3vF5/versions/nrqAIQFr/%21MoonlitPEM_2.1.3_FABRIC.jar',
        'path': 'files',
        'file': 'files/test4.jar',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }, {
        'name': 'test_download_5',
        'url': 'https://cdn.modrinth.com/data/SFQA3vF5/versions/nrqAIQFr/%21MoonlitPEM_2.1.3_FABRIC.jar',
        'path': 'files',
        'file': 'files/test5.jar',
        'size': 0,
        'hash': {
            'hash_type': 'sha1',
            'hash_value': 'b4fec680269af21b1c6a4c3f41fc1a725cf5499b'
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }, {
        'name': 'test_download_6',
        'url': 'https://curl.se/download/curl-8.9.1.tar.gz',
        'path': 'files',
        'file': 'files/curl-8.9.1.tar.gz',
        'size': 0,
        'hash': {
            'hash_type': '',
            'hash_value': ''
        },
        'lock': Lock(),
        'progress': 0,
        'status': 'NotAdded',
        'timestamp': {
            'start': 0.0,
            'end': 0.0
        }
    }]

    # 创建下载器
    zDownloader = DownloaderThreadPool(
        Name="TestDownloader",
        NumPools=3,
        PoolSize=2,
        QueueSize=5
    )

    # 添加任务
    for Task in Tasks: zDownloader.AddTask(Task)

    # 检查任务状态
    while True:
        sleep(1)
        if all([Task['status'] == 'Completed' or Task['status'] == 'Failed' for Task in Tasks]):
            break
    
    for n in range(100):
        sleep(0.1)

    # 关闭下载器
    RemainingTasks = zDownloader.Shutdown()