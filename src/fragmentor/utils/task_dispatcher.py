# encoding=utf-8
# authoring=lyapunov
import hashlib
import os
from datetime import datetime as dt
import time

from bpy_scripts.blend_loader import BlendLoader
from bpy_scripts.randomizor import Randomizor
from bpy_scripts.generator import Generator

from utils.config_loader import ConfigLoader
from utils.logger import info
from utils.singleton import Singleton
from utils.log_writer import LogWriter


@Singleton
class TaskDispatcher():
    def __init__(self):
        self._bll = BlendLoader()
        self._cfl = ConfigLoader()
        self._rdr = Randomizor()
        # self._ldr = LabelDumper()
        self._grr = Generator()
        self._time_start = time.time()
        self._time_last = self._time_start
        self._hash_name = dt.now().strftime('output_%Y-%m-%d-%H-%M-%S')
        log_base_path = os.path.join(self._cfl.get('paths/output'), self._hash_name, 'logs') 
        self._lwr = LogWriter().set_base_path(log_base_path)


    def dispatch_one(self):
        '''
        Dispatch and execute one task.
        '''
        name = dt.now().strftime('item_%Y-%m-%d-%H-%M-%S')
        self._lwr.initialize(name)
        # name = hashlib.md5(dt.now().strftime('%Y-%m-%d %H:%M%S').encode('utf-8')).hexdigest()
        # 1. 导入模型
        classification, blend_path = self._rdr.get_random_files()
        mode_col = self._cfl.get('names/model-collection')
        info(f'Open blend file {blend_path}.')
        if blend_path:
            self._bll.append_collections(blend_path, mode_col)
        # 2. 开始渲染
        output_path = os.path.abspath(os.path.join(self._cfl.get('paths/output'), self._hash_name, 'images', name + '.png').replace('\\', '/'))
        print(output_path)
        res = self._rdr.randomize_all()
        self._grr.generate_one(output_path)

        # 写入日志.
        time_now = time.time()
        self._lwr.update('time-total', time_now - self._time_start)
        self._lwr.update('time-perse', time_now - self._time_last)
        self._time_last = time_now

        res['name'] = name
        res['model-path'] = blend_path
        res['cls'] = classification 

        self._lwr.update_many(res)

        self._lwr.write_one()
        return res

    def get_one_model(self): 
        '''
        Randomly get a model from assigned paths.
        Return with a label recording the
        '''

    def get_start_time(self):
        return self._time_start
    def get_hash_name(self):
        return self._hash_name