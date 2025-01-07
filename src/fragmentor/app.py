from datetime import datetime as dt

from utils.config_loarder import ConfigLoader
from bpy_scripts.blend_loader import BlendLoader
from utils.task_dispatcher import TaskDispatcher


class App():
    ''''''
    def run(self):
        print('hello, mir4ge!')
        self.initialize()
        self.start_event_loop()
    
        

    def initialize(self):
        '''
        Initialize before program starts.
        '''
        # 读取参数设置.
        self._cfl = ConfigLoader()
        # 加载默认场景.
        print( self._cfl.get('paths/blend-folder'))
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
        self.tdp = TaskDispatcher()
        start = dt.now()
        prefix = start.strftime('output_%d-%m-%Y-%H-%M-%S')
        count = self._cfl.get('experiments/count')
        idx = 0
        for i in range(count):
            self.tdp.dispatch_one(f'{prefix}/img-{i}')
            print(f'{i + 1} of {count} render finished.')
            print(f'Sum up to {(dt.now() - start).seconds} seconds elapsed.')
            idx += 1
            if idx > 10:
                self._bll = BlendLoader().load_blend_file(self._cfl.get('paths/blend-folder') + '/' + 'main.blend')
                idx -= 10