import tracemalloc
import time

from bpy_scripts.blend_loader import BlendLoader
from utils.config_loader import ConfigLoader

from utils.logger import Logger, info
from utils.singleton import Singleton
from utils.task_dispatcher import TaskDispatcher


class App():
    ''''''
    def run(self):
        info('hello, mir4ge!')
        self.initialize()
        logger = Logger()
        # logger.append_sink(None)
        self.start_event_loop()
        # LabelDumper().monitor_start()
        # print(self._cfl.contains('paths/label-output'))


    def initialize(self):
        '''
        Initialize before program starts.
        '''
        self._monitor = AppMonitor()
        # 读取参数设置.
        self._cfl = ConfigLoader()
        # 加载默认场景.
        self._bll = BlendLoader().load_blend_file(self._cfl.get('paths/blend-folder') + '/' + 'main.blend')



    def start_event_loop(self):
        tdp = TaskDispatcher()
        count = self._cfl.get('experiments/count')
        idx = 0
        for i in range(count):
            tdp.dispatch_one()
            info(f'{i + 1} of {count} render finished.')
            info(f'Sum up to {time.time() - tdp.get_start_time()} seconds elapsed.')
            idx += 1
            if idx > 10:
                self._bll = BlendLoader().load_blend_file(self._cfl.get('paths/blend-folder') + '/' + 'main.blend')
                idx -= 10

        

@Singleton
class AppMonitor():
    def __init__(self):
        tracemalloc.start()

    def output(self):
        info(tracemalloc.get_traced_memory())
    