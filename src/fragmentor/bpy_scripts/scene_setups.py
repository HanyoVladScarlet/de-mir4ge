import math


from bpy_scripts.blend_loader import BlendLoader, AssetNotFoundException


class SceneSetups():
    def __init__(self):
        self._bll = BlendLoader()

    def set_camera_look_at(self, rotation, centric_point, distance, cam_name):
        '''
        
        '''
        o_camera = self._bll.get_object(cam_name)
        if not o_camera:
            raise AssetNotFoundException('camera', cam_name)
        o_camera.location.x = distance * math.sin(rotation.x) * math.sin(rotation.z)
        o_camera.location.y = -distance * math.sin(rotation.x) * math.cos(rotation.z)
        # 直流分量是为了防止物体的中心点不在原点
        o_camera.location.z = distance * math.cos(rotation.x)
        o_camera.location += centric_point
        o_camera.rotation_euler = rotation
        
        return self

    def set_lighting(self, rotation, sun_intensity, env_intensity, sun_name):
        '''
        Note sun_intensity and env_intensity are mathutils.Vector
        '''
        o_sun = self._bll.get_object(sun_name)
        if not o_sun:
            raise AssetNotFoundException('object', sun_name)
        o_sun.rotation_euler = rotation
        return self