import os.path
from utils.singleton import Singleton
from utils.config_loarder import ConfigLoader


@Singleton
class FileWriter():
    def __init__(self, name):
        self._cfl = ConfigLoader()
        self.root = os.path.join(self._cfl.get('paths/output'), name)
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def write_infos(self, info):
        name = os.path.join(self.root, 'infos.json')
        with open(name, 'w+') as f:
            f.write(info)
        return

    def write_label(self, labels):
        name = os.path.join(self.root, 'labels.json')
        with open(name, 'w+') as f:
            f.write(labels)
        return