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
A fixed number of rounds are provided for each HIT. A round is what the crowdworker can see at one instant of time when working on our HIT. A round for step 1 contains 3 images of the object and asks crowdworkers to generate question-answer pairs that describe the images. A round for step 2 containts 6 images of the object and asks crowdworkers to generate more answers for the questions generated by phase 1 workers.

The code for the round generator module can be found in <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/views/roundsgenerator.py>`users.views.roundsgenerator`</a>. The purpose of this module is to select images and questions to generate rounds for the crowdworkers to play. The goal is to minimize the possibility that two crowdworkers answer the same imageset. All of these round generation operations are <a href=https://stackoverflow.com/questions/52196678/what-are-atomic-operations-for-newbies>atomic</a>. This is done to prevent round generation by one crowdworker from interfering with round generation of another crowdworker and messing up the database.

#### Step 1 Round Generation
I will first talk about <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/views/roundsgenerator.py#L39>`popGetList`</a>, which is used to create rounds for step 1. This function is called when a crowdworker accesses a new round of step 1.

When the first crowdworker enters the page, a list of all the ids of every availible image for the class that we are testing is generated and shuffled. This list is the queue of all answerable images. When a crowdworker enters the page, we dequeue the first 3 images in the queue and show them to the crowdworker. This queue is stored in the `get` attribute of a <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/models.py#L161>`Phase`</a> object that is stored in the database. When a crowdworker gives an answer for an image, the image id is added to the `post` attribute of the same `Phase` object.

In the case that a crowdworker leaves the page without giving an answer, there will be left over images that are not present in the `get` list (queue) or the `post` list. In that case, we recycle these unused images and put them back in `get` after we shuffle them in the same manner that we did when the first crowdworker joined. Since the first crowdworker's login is a special case of this recycling of images (`post` is empty), there is no special code in `popGetList` to deal with the first crowdworker. The recycling code is succinctly shown below.
```python
if len(getList) < count:
    nextImage = getList
    count -= len(getList)
    # Create a new GET list if necessary
    postList = rounds.post
    getList = [i for i in fullList if i not in postList and i not in nextImage]
    random.shuffle(getList)
    # if recycle and len(getList) < count: # old, unused code that can be removed
    #      rounds.post = []
    #     getList = [i for i in fullList if i not in nextImage]
    #     random.shuffle(getList)
else:
    nextImage = []
```
The first thing it does is see if `get` is empty (or doesn't have enough images to display to the crowdworker). If it is, then it recycles the images not yet answered by the workers (finding which ones are unused and shuffling the list). It it isn't, no recycling takes place.

<a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/views/roundsgenerator.py#L15>`pushPostList`</a> saves the image ids that were seen and answered by crowdworkers into the `post` attribute of `Phase`. This makes it impossible for `popGetList` to recycle the images when `get` runs out. Together, these two functions handle the generation of rounds for step 1.

#### Step 2 Round Generation
Step 2 is more complex than step 1 in terms of round generation. This is because crowdworkers are served question-imageset pairs instead of just imagesets. Ultimately, this round generator is similar to the step 1 generator, but using the same approach would require ![equation](http://www.sciweavers.org/tex2img.php?eq=\mathcal{O}(NQ)&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=) space where N is the number of imagesets and Q is the number of questions, which would have been infeasible using our database.

Instead, we approximate the same method by finding the image set that is least shown to workers and choosing the questions that were not answered for that imageset. Recycling is not done in step 2 to optimize the speed and space usage at the expense of some crowdworkers seeing the same imageset-question pair as another crowdworker. By tallying how many workers answer each imageset, we minimize the possibility that this happens, although we cannot avoid it due to the approximation.

First, space is allocated in the database for each imageset. An imageset is generated by creating a list of all of the image ids, shuffling, and partitioning into groups of 6. Unlike with step 1, this only happens the first time the step is opened by a crowdworker. Remember that no recycling is done. A `get` and `post` list, each of size N (number of imagesets), is created here.

```python
rounds, isNew = Phase.objects.select_for_update().get_or_create(phase='2')
if isNew:
    imgsets = list(ImageModel.objects.filter(img__startswith=settings.KEYRING).values_list('id', flat=True))
    postLen, trunLen = divmod(len(imgsets), 6)

    # Truncate shuffled list to a multiple of 4 length
    random.shuffle(imgsets)
    if trunLen:
        del imgsets[-trunLen:]
    rounds.imgset = imgsets

    # Create empty list to store image set gets
    rounds.get = [0] * postLen

    # Create empty list to store image set posts
    rounds.post = [0] * postLen
    rounds.save()
```

After space is allocated for the `get` and `post` lists, the least answered imageset (minimum value of `post`) is located by using a `for` loop. In the case of a tie, the least shown imageset (minimum value of `get`) is given out of the imagesets with the minimum value of `post`.

```python
# Find the least answered image sets
# Find minimum answered image set
imin = -1
getMin = 900000
postMin = 900000
for i, (get, post) in enumerate(zip(rounds.get, rounds.post)):
    # This if statement is the one that minimizes post and get in the way described in the above paragraph
    if (post < postMin) or post == postMin and get < getMin:
        imin, getMin, postMin = i, get, post

# If every image was answered the correct number of times, stop
if postMin >= numQs:
    break
```

After the least answered imageset is found, the a random non-answered question for that imageset is found. To find all non-answered questions, we find all questions that are final (not marked as duplicate by the NLP) and remove all questions that have answers on them that have been made on the select imageset. The questions that have answers on the current imageset are found by `Answer.objects.filter(imgset=imin).values_list('question_id', flat=True)`. `filter` selects the answers that have been made on the current imageset and `values_list` gets the question to which each answer has been made.

Once the list of all questions that have not been answered yet has been made, it is shuffled and the top two questions are selected to be shown on the round. Once this is done, a new question-imageset pair has been selected and will be shown to the crowdworker.

```python
# Find the first available question for the imageset
qset = Question.objects.filter(Q(isFinal=True) & ~Q(id__in=Subquery(
    Answer.objects.filter(imgset=imin).values_list('question_id', flat=True)
))).order_by('?')
questions.extend(qset[:2])

rounds.get[imin] += 1
imgs.append(rounds.imgset[6*imin:6*imin+6])
sets.append(imin)
if len(qset) > 1:
    sets.append(imin)
```

`step2_push` works in the same way as `pushPostList`. The only thing different is that it keeps track of the number of questions answered for each imageset instead of if the imageset has been shown. This means that an imageset will be shown to a crowdworker until it runs out of questions. At which point, the imageset will not be shown to crowdworkers anymore. 

### player_required decorators
The original purpose of the <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/decorators.py#L18>`player_required`</a> decorator was to authenticate a player and ensure they were logged into MTurk. It was much more convienient to handle processing of MTurk HIT metadata in the decorator instead of the individual views because it reduced the duplication of code.

The decorator reads URL parameters given to it by MTurk (specifically <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/decorators.py#L39-L43>'assignmentId', 'hitId', and 'workerId'</a>). These parameters are stored into a <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/models.py#L207>`HIT`</a> object. This `HIT` object will keep track of the number of rounds that were completed by each worker. If the worker finishes the necessary number of rounds needed to complete a HIT, <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/decorators.py#L45-L48>they will be redirected to the completion page</a>. Otherwise, they are shown the next round of their HIT. This management of the HIT object and Murk HIT completion is the essence of the `player_required` decorator.

### Crowd worker Hit Session Control
The <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/admin.py#L375>`HITAdmin`</a> class allows for convienient approval or rejection of crowdworker assignments inside of the Django Admin interface.

Approvals and rejections are sent directly to MTurk through Amazon's Boto API (https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/admin.py#L491-L570). The satus of a HIT is calculated by the data stored into the `HIT` object in the database by the `player_required` decorator.

Once a HIT is completed and sent to MTurk, the status of the HIT is change to complete. We donote this with a grey question mark in the GUI. After we approve a HIT, the status changes to approved and the question mark becomes a green check. If we hit reject, the status changes to rejected and a red X is shown. The code to do this in the <a href=https://github.com/PurdueCAM2Project/Crowdsourcing/blob/5aa6935d6268aff068e5f7854d2f976f84443175/users/admin.py#L449-L475>`status`</a> property of the admin.
```c
//Todo: This should be documented by Ani
```

## Other Notes
* When you work on your own assignment, please open a new branch and make a pull request after you push to __your own branch__. Do not work on master!!!

* Since the local development database is shared among the group, please do not delete the image objects as it might create get other people's testing unsynchronized.
