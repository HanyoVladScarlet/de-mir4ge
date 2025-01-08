from datetime import datetime as dt

# from utils.config_loarder import ConfigLoader
from utils.paths import join_paths
from utils.singleton import Singleton


@Singleton
class Logger():
    def __init__(self):
        self._log_file = None
        self._verbose_level = -1
        self._count = 0
        self._output_path = None
        self._name = None
        self._sinks = []

    def _write(self, item):
        if 'level' in item and item['level'] <= self._verbose_level:
            return
        if not self._log_file or self._count > self._cfl.get('logger/console/max-count'):
            name = join_paths(self._name, dt.now().strftime('%Y-%m-%d-%H-%M-%S'))
            self._open_log(name)
        
    def _open_log(self, name):
        if self._log_file:
            self._log_file.close()
        path = join_paths(self._cfl.get('paths/log-output'), name + '.log')
        self._log_file = open(path)
        return self
    
    def append_sink(self, sink):
        if sink in self._sinks:
            print(f'Sink `{type(sink)}`')
            return self
        self._sinks.append(sink)
        return self

    def log(self, args):
        for sink in self._sinks:
            # if not sink:
            #     warn(f'Not supported sink `{type(sink).name}`.')
            try:
                sink.log(args)
            except Exception as e:
                print(f'Sink caught an error\n{e}')


class LoggerSink():
    def __init__(self, name):
        self.name = name
        return
    def sink(self, args):
        return


class FileSink(LoggerSink):
    def __init__(self, name):
        super().__init__(name)
        self._enable = False
        return
    def sink(self, args):
        if not self._enable:
            return
        
        return super(args).sink(args)


_logger = Logger()


PREF_R = '\033[31m'
PREF_G = '\033[32m'
PREF_Y = '\033[33m'
SUFF = '\033[0m'

def console_output(input, level):
    now = dt.now()
    _logger.log({
        'lv': level,
        'msg': input,
        'tsp': now.timestamp()
    })
    input = f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] {input}'
    if level == -1:
        print(input)
    if level == 0:
        print(PREF_G + input + SUFF)
    if level == 1:
        print(PREF_Y + input + SUFF)
    if level == 2:
        print(PREF_R + input + SUFF)
    return 

def log(msg):
    console_output(msg, -1)
    return

def info(msg):
    console_output(msg, 0)
    return

def warn(msg):
    console_output(msg, 1)
    return

def error(msg):
    console_output(msg, 2)
    return