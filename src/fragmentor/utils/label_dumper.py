# coding=utf-8
import os
import threading

from utils.config_loarder import ConfigLoader
from utils.paths import join_paths

'''
这个模块用于将标签信息导出.
设置可供选择的标签存储方式.
'''

class LabelDumper():
    '''
    '''
    def __init__(self):
        self._cfl = ConfigLoader()
        
    def label_one(self, name, msg):
        base_path = self._cfl.get('paths/label-output') if self._cfl.contains('paths/label-output') else '/de-mir4ge'
        output_path = join_paths(base_path, name)
        with open(output_path, 'w+') as f:
            f.write(msg)
        return