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
        self.cfl = ConfigLoader()
        # 加载默认场景.
        print( self.cfl.get('paths/blend-folder'))
        self._bll = BlendLoader().load_blend_file(self.cfl.get('paths/blend-folder') + '/' + 'main.blend')


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
        self.tdp.dispatch_one('hao!')