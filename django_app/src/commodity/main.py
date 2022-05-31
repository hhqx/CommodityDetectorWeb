import time

# define method
from django import forms
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


from pathlib import Path



def save_file(file, name=None):
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

def save_img_to_local(img1, img2):
    path1 = save_file(img1, name='up1.jpg')
    path2 = save_file(img2, name='up2.jpg')
    return path1, path2

def detect_commodity(path1, path2,
                     config={'nms_thresh': 0.02, 'iou_thresh': 0.2}):
    from yolox import Object_Detection
    OD = Object_Detection(str(path1), str(path2),
                           config=config
                           )
    pathout, results, table = OD.detect()

    info = results
    out1 = Path(pathout[0])
    out2 = Path(pathout[1])

    return info, out1, out2, table


#-----------------ObjectDetection---------------------

class InputForm(forms.Form):
    img1 = forms.ImageField(label='Image 1')
    img2 = forms.ImageField(label='Image 2')

class ConfigForm(forms.Form):
    nms_thresh = forms.FloatField()
    iou_thresh = forms.FloatField()

# -----------------handle post request---------------------
# handle post request
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render

from django.conf import settings

def inputForm(request, *args, **kwargs):
    info = ''
    context = dict()
    context['interactive_message'] = 'initializing..'
    timestamp = f"?t={round(time.time())}"
    context['detectors'] = dict({'img1urls': settings.MEDIA_URL + 'up1.jpg' + timestamp,
                                 'img2urls': settings.MEDIA_URL + 'up2.jpg' + timestamp,
                                 })
    context['results'] = dict({'img1urls': settings.MEDIA_URL + 'up1--out.jpg' + timestamp,
                                 'img2urls': settings.MEDIA_URL + 'up2--out.jpg' + timestamp,
                                 })
    if request.method == 'POST':
        form1 = InputForm(request.POST, request.FILES)
        form2 = ConfigForm(request.POST)
        # check whether it's valid:
        if form1.is_valid():
            data = form1.cleaned_data
            print(data)

            context['interactive_message'] = 'success submit！'
            path1, path2 = save_img_to_local(data['img1'], data['img2'])
            context['detectors'] = dict({'img1urls': settings.MEDIA_URL + os.path.split(path1)[1] + timestamp,
                                         'img2urls': settings.MEDIA_URL + os.path.split(path2)[1] + timestamp,
                                         })

        elif form2.is_valid():
            config = form2.cleaned_data
            path1 = os.path.join(settings.MEDIA_ROOT, 'up1.jpg')
            path2 = os.path.join(settings.MEDIA_ROOT, 'up2.jpg')
            context['detectors'] = dict({'img1urls': settings.MEDIA_URL + os.path.split(path1)[1] + timestamp,
                                         'img2urls': settings.MEDIA_URL + os.path.split(path2)[1] + timestamp,
                                         })
            info, out1, out2, table = detect_commodity(path1, path2, config=config)
            context['results'] = dict({'img1urls': settings.MEDIA_URL + str(out1.name) + timestamp,
                                       'img2urls': settings.MEDIA_URL + str(out2.name) + timestamp,
                                       'info': info
                                       })
            context['table'] = table
            context['interactive_message'] = f'success calculation！config: {config}'

        else:
            context['interactive_message'] = "POST failed, please try again!"

    # TODO: add a slide to select different example pair
    print(f"interactive_message: {context['interactive_message']}")
    return render(request, 'my/index.html', context,)