import os
import json
from threading import Lock

from utils.singleton import Singleton


@Singleton
class LogWriter():
    def __init__(self):
        self._base_path = None
        self._name = None
        self._content = None
        self._lock = Lock()
    
    def initialize(self, name):
        self._name = name
        self._content = {}
        return self

    def write_one(self):
        if not self._base_path:
            raise Exception('Set `BASE PATH` before write a log.')
        output_path = os.path.join(self._base_path, self._name + '.json')
        with open(output_path, 'w+') as f:
            f.write(json.dumps(self._content))
        return self

    def update(self, key, val):
        with self._lock:
            if self._content is None:
                raise Exception('Log writer did not initialize.')
            self._content[key] = val
            return self

    def update_many(self, many):
        for k in many.keys():
            self.update(k, many[k])
        return self

    def get(self, key):
        if self._content is None:
            raise Exception('Log writer did not initialize.')
        if not key in self._content:
            return
        return self._content[key]
    
    def keys(self):
        if self._content:
            return self._content.keys()
        return

    def delete(self, key):
        val = self.get(key)
        if val:
            self._content.__delitem__(key)
        return val

    def set_base_path(self, base_path):
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        self._base_path = base_path
        return self