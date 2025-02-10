import bpy
import os



FILE_PATH = 'C:/Users/Lyapunov/Documents/Hatuki/Github/de-mirage/src/fragmentor/assets/models/mid-size-truck/Toyota_Hilux_(Mk2)_1972.blend'
# COL_NAME = 'model'
AXIS_NAME = 'bounding_box'


def append_col():
    file_path = os.path.abspath(FILE_PATH)
    axis = bpy.data.objects.get(AXIS_NAME)
    if axis:
        bpy.data.objects.remove(axis, unlink=True)
    with bpy.data.libraries.load(file_path) as (data_from,data_to):
        if AXIS_NAME in data_from.objects:
            data_to.objects.append(AXIS_NAME)
    axis = bpy.data.objects.get(AXIS_NAME)
    if axis:
        print(f'location: {axis.location}, dimension: {axis.scale}')
    return


if __name__ == '__main__':
    append_col()