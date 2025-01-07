import bpy

from utils.config_loarder import ConfigLoader


class Generator():
    instance = None
    @staticmethod
    def get_instance():
        if Generator.instance == None:
            Generator.instance = Generator()
        return Generator.instance

    def __init__(self):
        self._cfl = ConfigLoader()

    def render_one(self, path):
        bpy.context.scene.frame_set(83)
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(path)
        return

    def generate_one(self, name):
        self.render_one(self._cfl.get('paths/output') + name + '.png')

        return