from datetime import datetime as dt
import tracemalloc

from bpy_scripts.blend_loader import BlendLoader
from utils.config_loarder import ConfigLoader
from utils.label_dumper import LabelDumper
from utils.logger import Logger, info
from utils.singleton import Singleton
from utils.task_dispatcher import TaskDispatcher


class App():
    ''''''
    def run(self):
        info('hello, mir4ge!')
        self.initialize()
        logger = Logger().append_sink(None)
        self.start_event_loop()
        # LabelDumper().monitor_start()
        

    def initialize(self):
        '''
        Initialize before program starts.
        '''
        self._moniter = AppMonitor()
        # 读取参数设置.
        self._cfl = ConfigLoader()
        # 加载默认场景.
        self._bll = BlendLoader().load_blend_file(self._cfl.get('paths/blend-folder') + '/' + 'main.blend')



    def start_event_loop(self):
        # if not self.cfl.check_loaded():
        #     print('Load config before task execution.')
        #     return
        # count = self.cfl.get('experiments/count')
        # res = []
        # for i in range(count):
        #     res.append(i)
        # print(res)
        tdp = TaskDispatcher()
        start = dt.now()
        prefix = start.strftime('output_%d-%m-%Y-%H-%M-%S')
        count = self._cfl.get('experiments/count')
        idx = 0
        for i in range(count):
            tdp.dispatch_one(f'{prefix}/image/img-{i}')
            info(f'{i + 1} of {count} render finished.')
            info(f'Sum up to {(dt.now() - start).seconds} seconds elapsed.')
            info(self._moniter.output())
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
    