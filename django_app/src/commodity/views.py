# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import time
import random

from django.conf import settings
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from commodity.utils.utils import PickleData

MAX_PAGE = 6

############### Config ###############
class ConfigForm(forms.Form):
    nms_thresh = forms.FloatField()
    score_thresh = forms.FloatField()
    # test = forms.FloatField()
CONFIG_KEYS = list(ConfigForm.base_fields.keys())
class ConfigClass:
    """" load or save config data"""
    def __init__(self):
        keys = CONFIG_KEYS
        default = 0
        config = dict()
        for k in keys:
            config[k] = default
        self.config = config

    def load(self, name="default"):
        # load from local file
        try:
            config_set = PickleData().load(name='config')
        except:
            config_set = dict()

        all_keys = list(self.config.keys())
        for k,v in config_set.items():
            if k in all_keys:
                self.config[k] = v
        pass
        return {"name": list(self.config.keys()),
                "value": list(self.config.values()),
                "dict": self.config,
                }
    def save(self, config, name="default"):
        Pickle = PickleData()
        Pickle.save(config, name='config')
        pass

############### Tools ###############
def path_local_to_media(path):
    """ convert local path to media path"""
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
        rpath = p.relative_to(settings.MEDIA_ROOT)
        print(rpath)
    except ValueError:
        print("path not in MEDIA_ROOT !")
        raise ValueError(f'path not in MEDIA_ROOT ! ')
        return None
    mpath = os.path.join(settings.MEDIA_URL, rpath)
    return mpath

def select_test_pairs(index, db_path=None):
    path1 = os.path.join(settings.MEDIA_ROOT, 'before.jpg')
    path2 = os.path.join(settings.MEDIA_ROOT, 'after.jpg')
    index = index % MAX_PAGE + 1

    path1 = os.path.join(settings.MEDIA_ROOT, f'db/{index}/{"1.jpg"}')
    path2 = os.path.join(settings.MEDIA_ROOT, f'db/{index}/{"2.jpg"}')

    return path1, path2

def default_page_context(nowpage, **kwargs):
    context = {}
    context['config_set'] = ConfigClass().load()
    timestamp = f"?t={round(time.time())}"
    context['ctrl'] = dict({"timestamp": timestamp,
                            "nowpage": nowpage,
                            "prevpage": max(nowpage - 1, 1),
                            "nextpage": nowpage % MAX_PAGE + 1,
                            "randpage": random.randint(1, MAX_PAGE)})
    path1, path2 = select_test_pairs(nowpage)
    context['detectors'] = dict({'img1urls': path_local_to_media(path1),
                                 'img2urls': path_local_to_media(path2),
                                 })
    return context

def page_get(request, **kwargs):
    nowpage = kwargs['page']
    context = default_page_context(nowpage)
    return render(request, 'my/index_page.html', context, )



############### UploadClass ###############
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path

class InputForm(forms.Form):
    img1 = forms.ImageField(label='Image 1')
    img2 = forms.ImageField(label='Image 2')
class UploadClass:
    def __init__(self):
        pass

    def save_file(self, file, name=None):
        """ Save Django InMemoryUploadedFile """
        data = file
        name = name if name is not None else file.name
        file_name = os.path.join(settings.MEDIA_ROOT, name)
        # file_name = MEDIA_ROOT
        print(file_name)
        if os.path.exists(file_name):
            os.remove(file_name)
        path = default_storage.save(file_name, ContentFile(data.read()))
        return Path(path)

    def save_img_to_local(self, img1, img2):
        path1 = self.save_file(img1, name='up1.jpg')
        path2 = self.save_file(img2, name='up2.jpg')
        return path1, path2

    def post(self, request, *args, **kwargs):
        form = InputForm(request.POST, request.FILES)
        data = form.cleaned_data if form.is_valid() else None
        print(data)
        context = default_page_context(1)

        context['interactive_message'] = 'success submit！'
        path1, path2 = self.save_img_to_local(data['img1'], data['img2'])
        context['detectors'] = dict({'img1urls': path_local_to_media(path1),
                                     'img2urls': path_local_to_media(path2),
                                     })
        context['ctrl']['isuploadpage'] = True
        return render(request, 'my/index_page.html', context, )

############### CalculateClass ###############
class CalculateClass:
    def __init__(self):
        pass
    def detect_commodity(self, path1, path2,config=None):
        from yolox import Object_Detection
        OD = Object_Detection(str(path1), str(path2),
                              config=config,
                              )
        pathout, results, table = OD.detect()

        info = results
        out1 = pathout[0]
        out2 = pathout[1]

        return info, out1, out2, table
    def post(self, request, *args, **kwargs):
        form = ConfigForm(request.POST)
        if form.is_valid():
            config = form.cleaned_data
            # save config data to local file
            ConfigClass().save(config)
        else:
            config = None
        page = kwargs['page']
        context = default_page_context(page)
        if "isuploadpage" in kwargs.keys():
            path1 = os.path.join(settings.MEDIA_ROOT, 'up1.jpg')
            path2 = os.path.join(settings.MEDIA_ROOT, 'up2.jpg')
            context['ctrl']['isuploadpage'] = True
        else:
            path1, path2 = select_test_pairs(page)

        info, out1, out2, table = self.detect_commodity(path1, path2, config=config)

        context['detectors'] = dict({'img1urls': path_local_to_media(path1),
                                     'img2urls': path_local_to_media(path2),
                                     })
        context['results'] = dict({'img1urls': path_local_to_media(out1),
                                   'img2urls': path_local_to_media(out2),
                                   'info': info,
                                   })
        context['table'] = table
        context['interactive_message'] = f'success calculation！config: {config}'
        return render(request, 'my/index_page.html', context, )

############### views ###############
def index(request, *args, **kwargs):
    return HttpResponseRedirect(reverse("commodity:page", kwargs={"page":1}))


def page(request, *args, **kwargs):
    return page_get(request, *args, **kwargs)

def calculate(request, *args, **kwargs):
    if request.method == "POST":
        handle = CalculateClass()
        response = handle.post(request, *args, **kwargs)
        return response
    elif request.method == "GET":
        response = page_get(request, page=kwargs['page'])
        return response

def upload(request, *args, **kwargs):
    if request.method == "POST":
        handle = UploadClass()
        response = handle.post(request, page=1)
        return response
    elif request.method == "GET":
        context = default_page_context(1)
        context['detectors'] = dict({'img1urls': settings.MEDIA_URL + 'up1.jpg',
                                     'img2urls': settings.MEDIA_URL + 'up2.jpg',
                                     })
        context['ctrl']['isuploadpage'] = True
        return render(request, 'my/index_page.html', context, )

def upload_calculate(request, *args, **kwargs):
    if request.method == "POST":
        response = calculate(request, page=1, isuploadpage=True)
        return response
