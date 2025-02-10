# encoding=utf-8
# author=lypunov
import os


def get_paths(paths):
    if paths and len(paths) > 0 :
        if type(paths[0]) == tuple:
            return paths[0]
        return paths
    raise Exception('Illegal path list.')



def join_paths(*paths):
    paths = get_paths(paths)
    res = []
    for path in regulate_paths(paths):
        res.extend(path.split('/'))
    return '/' if paths[0].startswith('/') else '' + '/'.join(res)

def regulate_paths(*paths):
    '''
    
    '''
    paths = get_paths(paths)
    for path in paths:
        s_path = path.replace('\\', '/')
        s_path = s_path.replace('￥', '/')
        yield s_path


def validate_paths(*paths):   
    paths = get_paths(paths)
    for path in paths:
        # Try to normalize the path
        normalized_path = os.path.normpath(path)
        # Check if the path contains illegal characters
        if set(r'<>:"/\|?*').intersection(normalized_path):
            return False
        # Check if the path is too long (over 255 characters)
        return False if len(normalized_path) > 255 else True


