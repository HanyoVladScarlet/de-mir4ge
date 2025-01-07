# encoding=utf-8
# authoring=lyapunov
from bpy_scripts.blend_loader import BlendLoader
from bpy_scripts.randomizor import Randomizor
from bpy_scripts.generator import Generator
from utils.config_loarder import ConfigLoader
from utils.label_dumper import LabelDumper
from utils.paths import join_paths
from utils.singleton import Singleton


@Singleton
class TaskDispatcher():
    def __init__(self):
        self._bll = BlendLoader()
        self.cfl = ConfigLoader()
        self._rdr = Randomizor()
        self._ldr = LabelDumper()
        self._grr = Generator()

    def dispatch_one(self, name):
        '''
        Dispatch and execute one task.
        '''
        # 1. 导入模型
        model_folder = join_paths(self.cfl.get('paths/blend-folder'), self.cfl.get('paths/model-folder'))
        blend_file = self._rdr.get_random_files(model_folder)
        print(f'Open blend file {blend_file}.')
        if blend_file:
            blend_path = join_paths(model_folder, blend_file)
            self._bll.append_collections(blend_path, 'model')

        print([o.name for o in self._bll.get_all_objects()])
        # 2. 设置参数
        res = self._rdr.randomize_all()
        # 3. 生成标签（这里是导出参数）
        print(res)
        self._ldr.dump(name, res)
        # 4. 开始渲染
        self._grr.generate_one(name)
        # print(f'Task `{name}` is done for execution.')