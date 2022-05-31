# from django.test import TestCase

# Create your tests here.
# from commodity.ObjectDetection.utils import PickleData
from django_app.src.commodity.utils.utils import PickleData


class mytest:
    def __init__(self):
        pass
    def test_form(self):
        Pickle = PickleData()
        form = Pickle.load('valid_form')
        print(form)
        pass
    def test_PickleData(self):
        testing_data = 'This is a testing data.'
        Pickle = PickleData()
        Pickle.save(testing_data)
        data = Pickle.load()
        print(data)
        pass


if __name__ == "__main__":
    test = mytest()
    # test.test_PickleData()
    # test.test_form() # failed

