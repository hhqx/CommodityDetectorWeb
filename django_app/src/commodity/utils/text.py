# from django.conf import settings
# from django_app.src.mysite import settings




import os
from pathlib import Path

from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
def path_local_to_media(path):
    path = os.path.abspath(path)
    print(path)
    # is existed
    if os.path.exists(path):
        mpath = path
        pass
    else:
        raise ValueError(f'path not exists ! ')
    # is in MEDIA_ROOT
    p = Path(path)
    try:
        rpath = p.relative_to(MEDIA_ROOT)
        print(rpath)
    except ValueError:
        print("path not in MEDIA_ROOT !")
        raise ValueError(f'path not in MEDIA_ROOT ! ')
        return None
    mpath = os.path.join(MEDIA_URL, rpath)
    return mpath

# print(os.path.abspath('../media/src'))

path = '../../media/src/up2--out.jpg'
media_path = path_local_to_media(path)
print(media_path)
# print(os.getcwd())

dir = os.path.join(settings.MEDIA_ROOT, 'db')
