import yaml
import os.path

from utils.logger import log, warn
from utils.singleton import Singleton 


CONFIG_PATH = 'src/reincarnator/config.yml'


# @Singleton
class ConfigLoader():
    '''
    Singleton.
    '''
    def __init__(self):
        self.conf = {}
        self._is_loaded = False
        if os.path.exists(CONFIG_PATH):
            self.load_config(CONFIG_PATH)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise Exception(f'Config path does not exist at `{config_path}`')

        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            self.conf = data
            self._is_loaded = True
            return self
    
    def get(self, key):
        keys = [k for k in key.split('/') if k.strip()]
        item = self.conf
        for k in keys:
            if not k in item:
                raise Exception(f'Wrong config path with {key}')
            item = item[k]
        return item
    
    def contains(self, key):
        keys = [k for k in key.split('/') if k.strip()]
        item = self.conf
        for k in keys:
            if not k in item:
                return False
            item = item[k]
        return True

    def check_loaded(self):
        '''
        False until self.read_config is called for the first time.
        '''
        return self._is_loaded


if __name__ == '__main__':
    cfl = ConfigLoader()
    print(cfl.get('/paths'))