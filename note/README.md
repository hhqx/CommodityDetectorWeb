# Django  Tutorial

# [Django documentation](https://docs.djangoproject.com/en/4.0/#django-documentation)

Everything you need to know about Django.

## [First steps](https://docs.djangoproject.com/en/4.0/#first-steps)

Are you new to Django or to programming? This is the place to start!

- **From scratch:** [Overview](https://docs.djangoproject.com/en/4.0/intro/overview/) | [Installation](https://docs.djangoproject.com/en/4.0/intro/install/)
- **Tutorial:** [Part 1: Requests and responses](https://docs.djangoproject.com/en/4.0/intro/tutorial01/) | [Part 2: Models and the admin site](https://docs.djangoproject.com/en/4.0/intro/tutorial02/) | [Part 3: Views and templates](https://docs.djangoproject.com/en/4.0/intro/tutorial03/) | [Part 4: Forms and generic views](https://docs.djangoproject.com/en/4.0/intro/tutorial04/) | [Part 5: Testing](https://docs.djangoproject.com/en/4.0/intro/tutorial05/) | [Part 6: Static files](https://docs.djangoproject.com/en/4.0/intro/tutorial06/) | [Part 7: Customizing the admin site](https://docs.djangoproject.com/en/4.0/intro/tutorial07/)
- **Advanced Tutorials:** [How to write reusable apps](https://docs.djangoproject.com/en/4.0/intro/reusable-apps/) | [Writing your first patch for Django](https://docs.djangoproject.com/en/4.0/intro/contributing/)

## Part 1: 
- Install requirements:
  
    ```shell
  pip install django==4.0
    
  ```
  
- Create Commodity APP:
    ```shell
    python manage.py startapp commodity 
    ```
    
- Edit **mysite/from django.urls import path, includeurls.py**, **polls/urls.py**, **polls/views.py** 

- Run Server at http://127.0.0.1:8000/polls/ :
    ```shell
    python manage.py runserver
    ```

## select from database
```shell
根据数据集图片对, 在url中用一个字段来表示测试序号, 例如: commodity/index/<num>/<cmd>
```

## Part 2: uploader

from: https://stackoverflow.com/questions/5871730/how-to-upload-a-file-in-django

- Create uploader

  ```
  python manage.py startapp uploader 
  ```


- Make changes to model

  ```
  # 同步数据库
  python manage.py makemigrations
  python manage.py migrate
  ```
- ImageField, https://docs.djangoproject.com/zh-hans/4.0/ref/forms/fields/



## 构建一张表单[¶](https://docs.djangoproject.com/zh-hans/4.0/topics/forms/#building-a-form)

#### 视图[¶](https://docs.djangoproject.com/zh-hans/4.0/topics/forms/#the-view)

假设您希望在您的网站上创建一张简易的表单，用来获取用户的名字。您需要在模板中使用类似代码：

```html
<form action="/your-name/" method="post">
    <label for="your_name">Your name: </label>
    <input id="your_name" type="text" name="your_name" value="{{ current_name }}">
    <input type="submit" value="OK">
</form>
```

这告诉浏览器将表单数据返回给URL `/your-name/` ，并使用 `POST` 方法。它将显示一个标签为 "Your name:" 的文本字段，以及一个 "OK" 按钮。如果模板上下文包含一个 `current_name` 变量，它会被预填充到 `your_name` 字段。

您需要一个视图来渲染这个包含HTML表单的模板，并能适当提供 `current_name` 字段。

提交表单时，发送给服务器的 `POST` 请求将包含表单数据。

现在，您还需要一个与该 `/your-name/` URL相对应的视图，该视图将在请求中找到相应的键/值对，然后对其进行处理。

这是一张非常简单的表单。实际应用中，一张表单可能包含数十上百的字段，其中许多可能需要预填充，并且我们可能希望用户在结束操作前需要多次来回编辑-提交。

我们可能需要在浏览器中进行一些验证，甚至在表单提交之前；我们可能希望使用更复杂的字段 ，以允许用户做类似日期选择等操作。

此刻，我们很容易通过使用Django来完成以上大部分工作。



...

## install package

- 安装打包好的本地包: django-polls, 需要在虚拟对应的环境中, 需要关闭代理
```shell
python -m pip install django-polls/dist/django-polls-0.1.tar.gz
```
- 卸载`django-polls`
```shell
python -m pip uninstall django-polls
```