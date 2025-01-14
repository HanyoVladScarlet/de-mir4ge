import os.path
from datetime import datetime as dt
from utils.singleton import Singleton
from utils.config_loarder import ConfigLoader


@Singleton
class FileWriter():
    def __init__(self, name):
        self._cfl = ConfigLoader()
        self._prefix = ''
        self.initialize()
        self._label_root = os.path.join(self._cfl.get('paths/output'), name, 'labels')
        self._root = os.path.join(self._cfl.get('paths/output'), name)
        if not os.path.exists(self._label_root):
            os.makedirs(self._label_root)

    def initialize(self, name=None):
        self._prefix = name if name else dt.now().strftime(f'%Y-%m-%d-%H-%M-%S')
        return self._prefix

    def write_infos(self, info):
        name = os.path.join(self._root, f'infos_{self._prefix}.json')
        with open(name, 'w+') as f:
            f.write(info)
        return self._prefix

    def write_label(self, labels):
        name = os.path.join(self._label_root, f'labels_{self._prefix}.json')
        with open(name, 'w+') as f:
            f.write(labels)
        return self._prefix