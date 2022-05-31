from django.contrib import admin

# Register your models here.

import inspect
from . import models

# 注册到admin
# admin.site.register(Author, )


# 注册所有model定义的到amdin界面
# 利用inspect包，筛选.models 中的 class
for (name, model) in inspect.getmembers(models, inspect.isclass):
    # print(name)
    pass
    # 注册该model到amin界面
    if str(model).find(__package__+".models") >= 0:
        admin.site.register(model, )
    # try:
    #     admin.site.register(model, )
    # except Exception as msg:
    #     print(msg)
    #     pass
    #     # print('model register error')

