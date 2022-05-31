import pickle

import os

from django import forms


class PickleData:
    """ a tool using pickle to save and load python variable """
    # data_folder = './pickle_data'
    default_folder = os.path.split(os.path.realpath(__file__))[0]
    data_folder = os.path.join(default_folder, 'pickle_data')
    def __init__(self):
        self.mkdir(self.data_folder)
        print(self.default_folder)
        pass
    def mkdir(self, path):
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
    def load(self, name='default'):
        filename = os.path.join(self.data_folder, name)
        # 以二进制读模式打开目标文件
        f = open(filename, 'rb')
        # 将文件中的变量加载到当前工作区
        storedlist = pickle.load(f)
        pass
        return storedlist
    def save(self, var={'test':'nothing'}, name='default', isprint=True):
        filename = os.path.join(self.data_folder, name)
        # 以二进制写模式打开目标文件
        f = open(filename, 'wb')
        # 将变量存储到目标文件中区
        pickle.dump(var, f)
        # 关闭文件
        f.close()
        if isprint:
            print(f'Has saved "{name}" at "{filename}".')
        pass
if __name__ == "__main__":
    testing_data = 'This is a testing data.'
    Pickle = PickleData()
    Pickle.save(testing_data)
    data = Pickle.load()
    print(data)

    class ConfigForm(forms.Form):
        nms_thresh = forms.FloatField()
        iou_thresh = forms.FloatField()
        test = forms.FloatField()

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

            for k,v in config_set.items():
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



if __name__ == '__main__':
    # load config data and print
    print(ConfigForm.base_fields.keys())
    config = ConfigClass().load(name='config')
    print(config)

