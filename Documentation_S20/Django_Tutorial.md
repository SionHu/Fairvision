# Crowdsourcing Backend: Django Framework Tutorial
## Introduction

This is the documentation of the CAM2 Crowdsourcing team's web application on backend image dataset, which will be useful for similar projects of the other

The documentation will briefly introduce how Django work but primarily focus on the specific implementation of our website.

## Django
__Django__ is the website backend of our crowdsourcing project and CAM2 official website: https://www.cam2project.net. It is a web framework written in python and uses a __Model-View-Template__ software design. Figure below shows how Django serves the website from the worker approach:

![Django MVT](https://mdn.mozillademos.org/files/13931/basic-django.png)

#### URLS
When there is a user (HTTP/HTTPS) request coming into our website, the `urls.py` inside the Django module will use Regex to parse the request. For example:

`urls.py`:
```python
path('', home.home, name='home'),
url(r'^profile/$', views.profile, name='profile'),
```

If user requests to our website with link [http(s)://ourdomaincom/](http(s)://ourdomaincom/), the Django backend can parse the path as `''` and thus forward to request to the view function `def home()` in `home.py`.

If user requests to link [http(s)://ourdomaincom/profile](http(s)://ourdomaincom/profile/), the regex function inside url can parse and match the `profile` and forward to function `views`

If there is no similar path or url found match, Django will redirect to `HTTP 404` page, which you can also customized.  

#### View
View is the most heavy module that will handle incoming calls from user request, retrieve the model from the database, and render the html file from the template and serve the webpage along with the data. Most of the logistics implementation will be focused on `views.py`.

#### Model
`models.py` is the abstract class Django provides without knowing the detail of relational database that the data is stored on. There is no need to call the query in Model should write and store any data input from users or read and serve people. Our user registration, images information (url, dataset name, class), By default, the database for local environment uses `SQLite`, but we uses Amazon RDS Server just to align with our production website that usually hosts on [Heroku](https://www.heroku.com/home) platform.

#### Template
Template folder contains everything for `views.py` to render. There are also some block styles you can pass from views to html for variable filling depend on the request.


Django has very clear documentation with good examples that can help you to know the projects and address the solution to the issue you might make. Please check their [documentation](https://docs.djangoproject.com/en/3.0/). There are also free Youtube tutorials for Django learning, do not hesitate to check those out too.

## Crowdsourcing Web App
As mentioned before, our website has 2 sites: development site and production site. 2 sites will contain different environment variables and parameters, but do not worry about it now. __Only the team leader or project admin can push the code to production site on Heroku__.

Our project uses a lot of AWS service: __Amazon Mturk__ for getting crowd workers, __RDS__ for database, __S3__ for image storage on cloud.

### Environment Setup

1. **Download the crowdsourcing repo from Github:**
`git clone https://github.com/PurdueCAM2Project/Crowdsourcing.git`

  Please make sure you have `python3` installed, as Django latest version is for python3.

2. **Download the python virtual environment**

  Type `pip install virtualenv` and type `virtualenv -p which python3.7 ~ <your_venv_name>/` to create a new virtual environment.

3. **Download and load the environment setup**

  All the sensitive password (e.g., AWS credentials) will be stored as environment variables so that 1. it is easy to use different setup according to different servers. 2. It is much more secured that way so that you do not need to upload this file along in git or cloud platform.

  Example file (new_env_var_cds.sh):
  ```
  export AWS_ACCESS_KEY_ID=AKIAUO554KZIXNEQI4IG
  export AWS_SECRET_ACCESS_KEY=fzoVkS2UUW/tOZIwb+tDGDBHORCk5y8rJUDz2yXm
  export AWS_STORAGE_BUCKET_NAME=develop-cds
  export IS_PRODUCTION_SITE=false
  export TEST_HTTP_HANDLING=false
  export POSTGRESQLPASS=cam2crowdsourcing!
  export NUMROUNDS=2
  export IS_GOOGLE_CLOUD=false
  ```

  This file is always shared on Crowdsourcing google drive folder or on Slack. Type `. new_env_var_cds.sh` to run the script first, and type `. <your_venv_name>/bin/activate` to activate your virtual environment for loading.

4. **Run server locally**
  Enter the crowdsourcing folder and you should see there is a file named `manage.py` and `requirement.txt`.

  1. Run `python -r requirement.txt` to install all the application dependencies into your virtual environment. (**!Note: This only needs to be done for the first time!**)

  2. Type `python manage.py` to run the server. Go to your browser and type 127.0.0.1:8080 to see the website.

### Application Specific Setup
There are some special setup in our previous crowdsourcing web application that might be useful for development consideration.

### AWS connection
All connection to AWS will be using boto3 api provided by Amazon.

In the Crowdsourcing folder there is a `csgame` folder which will be the application you created with Django. In the folder, there are 2 files need most attention: `settings.py` and `storage_backends.py`.

`settings.py` will load the Django setup. It contains the project root and set up connection to the database and cloud storage specified by our environment variables. It will also load the other modules & middleware of our main application, such as `users` which is a folder in crowdsourcing root path and contains the models and view logics. However, keep in mind that all the variables here cannot be modified during **runtime**. You can only import and use the environment variables defined in settings.py. If you want to change them while running the backend server, you will get runtime error.

`storage_backends.py` is our customized file where we defined the media storage path. It will make connection to s3 and contains a `MediaStorage` class to generate a url with the image.

To setup the s3 storage in `settings.py`:
```python
#Default file storage
DEFAULT_FILE_STORAGE = '<your_app_name>.storage_backends.MediaStorage'

```

#### Image Model  
In order to serve image from Amazon s3 and relates it to the input from users so that we can justify the crowd workers' work, we decided to create a model with Image. The image model will have a `img` parameter, which is the url of the image provided by s3:

```python
img = models.ImageField(verbose_name='Image', upload_to=get_upload_path, unique=True, validators=[validate_file_extension])
```
ImageField is the Django image database field type. upload_to is the function call which can find path to upload on Amazon S3 bucket with specific folders name. Validators will help validate the file format and make sure there is no invalid image names that would cause errors while we serve in Views.The image with question and answer database schema is shown below.

![Image Model](./database.png)

In the past project we used several datasets with different objects, but we do not want to delete the old images and re-upload new ones on S3 whenever we change the dataset to experiment. But image name will have the same `image_####` format starting from 1. Therefore we add a `class _UploadLock` which can help extract information with dataset name and object/class name when we upload images on admin site.

This is how it looks on admin site.

![Image Admin](./image_admin.png)

You can upload multiple images and decide the dataset name (called **Set**) and object name. It might take some time uploading, but after done you can go to Amazon S3 storage and find your file:

![Image S3](./image_S3.png)

However, as mentioned before, if specify
```python
KEY = my_env.get('KEY', 'Caltech101/airplanes/image_{:04d}.jpg')
```
then we cannot switch to other datasets during runtime. This might need to change for other purposes that might need multiple datasets usage.

#### Mturk File
Since we used [ExternalQuestion](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_ExternalQuestionArticle.html) that mturk will serve our website in the crowd worker's working frame, HIT could not be created directly on mturk and we had to use Api to make the calling. In the folder, there is a file named `mturk_hit.py` which can manage the HIT on mturk.

Type `python mturk_hit.py -h` to see all the usage.

Ani managed to make this management file appeared on admin page so no need to call on command. However, there were some bugs in the code so it could not function well. This details will be covered below.

#### Admin page
Admin page is another feature provided by Django. People with admin user status can go to `/admin` page and manage all the objects created from `models.py`.

To create an admin locally: type `python manage.py createsuperuser` and follow the instructions.

For production, let the team leader know and the leader will create one for you.

#### Form and Admin python
Next to `models.py` you might also see a file named `forms.py`. This is the file that determined the forms that can be rendered and valid directly without writing your own `<form></form>` in html and use `$.post` as our method does. We only use it to create user(player) registration form.

There is also a file, `admin.py`, which is the file to render the content that can be shown on admin site. Here it decides what model can be viewed and displayed, how will it save and create by admin. Please refer to Django documentation for more details.


#### POST Request from backend to frontend
Backend render to front-end is easy. But how to send Data back from user?

`HTTP POST` method will be using for sending data back. By calling from jQuery:

```javascript
// get the value of CSRF token
var CSRFtoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

//post method
$.post(window.location, {
    'imgnum': {{ imgnum|safe }},
    'data': resultArr,
    csrfmiddlewaretoken : CSRFtoken
    }, function(data){}).fail(function() {
  alert( "An error occurred. Could not submit your data." );
});
```
where `imgnum` is the template rendered variable provided by view; `data` is the javascript array object that store our workers' text inputs. The `csrfmiddlewaretoken` is a little different. This is the token that is required by Django for all form submission via post method, as it will detect whether the data is valid provided by a existing sessions, not from unknown hack attacks like DDOS.


The backend server should get the data in its `post` method:
```python
def phase01b(request, previewMode=False):
    # Only show people all the question and the answer. Keep in mind that people have the chance to click skip for different questions
    # There should be an array of question that got skipped. Each entry should the final question value
    # assignmentId = request.GET.get('assignmentId')
    if request.method == 'POST':
        # Get the answer array for different
        # Update the rounds posted for phase 01b
        imgsets = step2_push(request)
        #pushPostList(request, '²')
        dictionary = json.loads(request.POST.get('data[dict]'))

        # get the dictionary from the front-end back
        print("I got the QA dict: ", dictionary)

        for imgset, (question, answer) in zip(imgsets, dictionary):
            print("Answer: ", answer)
            # if the answer is not empty, add into database
            que = Question.objects.get(text=question, isFinal=True)
            new_Ans = Answer.objects.create(text=answer, question=que, hit_id=assignmentId, imgset=imgset)

        return HttpResponse(status=201)
```

### Round generator
```c
//Todo: This should be documented by Ani
```

### Crowd worker Hit Session Control
```c
//Todo: This should be documented by Ani
```

### player_required decorators
```c
//Todo: This should be documented by Ani
```

## Other Notes
* When you work on your own assignment, please open a new branch and make a pull request after you push to __your own branch__. Do not work on master!!!

* Since the local development database is shared among the group, please do not delete the image objects as it might create get other people's testing unsynchronized.
