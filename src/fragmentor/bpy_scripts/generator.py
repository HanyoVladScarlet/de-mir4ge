import bpy

from utils.config_loarder import ConfigLoader
from utils.singleton import Singleton



class Generator():
    def __init__(self):
        self._cfl = ConfigLoader()

    def render_one(self, path):
        bpy.context.scene.frame_set(83)
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(path)
        return

    def generate_one(self, name):
        file_path = self._cfl.get('paths/image-output') + name
        self.render_one(file_path)
        return file_path