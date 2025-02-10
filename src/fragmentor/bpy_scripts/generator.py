import bpy
import os

from utils.config_loader import ConfigLoader
from utils.singleton import Singleton



class Generator():
    def __init__(self):
        self._cfl = ConfigLoader()

    def render_one(self, path):
        bpy.context.scene.frame_set(83)
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(path)
        return

    def generate_one(self, file_path):
        self.render_one(file_path)
        return file_path