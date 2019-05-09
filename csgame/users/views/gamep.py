from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from users.models import NotSameVote, CustomUser, ImageModel, Label, Attribute, RoundsNum, listArray, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction

from django.contrib.auth.admin import UserAdmin

from django.http import HttpResponse

from django.shortcuts import render

# from ..forms import TestForm
import boto3
import botocore
from botocore.client import Config
import random
import json
from .roundsgenerator import rphase02

KEY = "airplanes/image_{:04d}.jpg"

@login_required
def phase01(request):
    # Some test
    # idk = ImageModel.objects.get(img='airplanes/image_0053.jpg')
    # print(idk.label.all())
    
    # number of rounds for image display
    rounds = RoundsNum.objects.filter(phase='phase01')
    
    if not rounds:
        # print('There is nothing, need to create new one')
        rounds = RoundsNum.objects.create(num=1)
        rounds.save()
        roundsnum = 1
    else:
        roundsnum = rounds.first().num
    
    # print("I got roundsNUM is: ", roundsnum)

    if roundsnum >= int(settings.NUMROUNDS) + 1:
        # print("The phase01 stops here")
        # push all to waiting page
        return render(request, 'over.html', {'phase': 'PHASE 01'})

    '''
    no random assignment for the images serving anymore. Assume dataset has been randomly cleared
    data = random.sample(range(1, 121), 4)
    '''
    
    # print("Url is: ", urls)

    if request.method == 'POST':
        roundsnum = RoundsNum.objects.filter(phase='phase01').first().num + 1
        RoundsNum.objects.filter(phase='phase01').update(num=roundsnum)
        data = request.POST.getlist('data[]')
#        print("I got data: ", data)
        img_list = request.POST.getlist('img_list[]')
#        print("I got the image num: ", img_list)
        key = "airplanes/image_"
        # Search fo r 
        for il in img_list:
            update_img = key + "{:04d}".format(int(il)) + ".jpg"
            # print("the label need to be stored in: ", update_img)
            model = ImageModel.objects.filter(img=update_img).first()
            if model:
                for d in data:
                    d = d.lower()
                    # print("Lower case: ", d)
                    # first iterate through whole label list
                    label = Label.objects.filter(name=d).first()
                    if label:
                    #    print("The exsiting label is: ", label)
                        # check if the image model contains that label
                        label.isTaboo = False
                        label.save()
                        lb = model.label.filter(name=d).first()
                        if lb:
                            pass
                        else:
                            model.label.add(label)
                    else:
                        label = Label.objects.create(name=d, isTaboo=False)
                        label.save()
                        model.label.add(label)
            else:
                print("not Found!")
        '''
        imgs = ImageModel.objects.all()
        for i in imgs:
            print("the name of each image is: ", i.img.name)
        '''
    data = [4 * roundsnum - 3, 4 * roundsnum - 2, 4 * roundsnum - 1, 4 * roundsnum - 0]
    
    KEYS = map(KEY.format, data)

    urls = [default_storage.url(KEY.format(id)) for id in data]

    instructions = Phase01_instruction.get_queryset(Phase01_instruction) or ['none']
    json_list = json.dumps(data)
    
    return render(request, 'phase01.html',{ 'url1': urls[0], 'url2': urls[1], 'url3': urls[2], 'url4': urls[3], 'json_list': json_list, 'instructions': instructions})

# View for phase02
@login_required
def phase02(request):
    # For post method, modify the labels of imagemodel only, only save models when the index number array runs out
    showbutton = True
    print("Current user is: ", request.user.email)
    if request.method == 'POST':
        
        # get the not-same button from the user
        notsamebutton = request.POST.get("data") == "1"
        
        # if someoneclick the button, which means player think they are unique, then do nothing and leave them in the same page.
        if notsamebutton:
            # This is the solution for April celecbration, not the final design for Amazon Turk
            # Count the number of players that are not superuser
            totalplayer = CustomUser.objects.all().exclude(is_superuser=True)
            threshold = int(float(len(totalplayer)) * 0.8)
            
            # stop if the threshold are met by the number of votes
            voteNum = NotSameVote.objects.all().first()
            if not voteNum:
                votelist = [request.user.email]
                voteNum = NotSameVote.objects.create(email=votelist, vote=1)
                voteNum.save()
            else:
                playerlist = voteNum.email
                if request.user.email in playerlist:
                    pass
                else:
                    playerlist.append(request.user.email)
                    voteNum.vote += 1
                    voteNum.save()
            print("Current number of vote: ", voteNum.vote)
            if voteNum.vote >= threshold:
                print("Generate stop instance")
                phasebreak = PhaseBreak.objects.get(phase='phase02')
                phasebreak.stop = True
                phasebreak.save()
                print("Finish Setting break phase now")
            
        else:
            # Get the card names as a list from front-end
            newlabels = request.POST.getlist('newlabels[]')
            # print("new labels for storage: ", newlabels)
        
            # remove the prvious manytomany labels and attach new list
            remainIndex = request.POST.get('remainIndex')
            delIndices = request.POST.getlist('delIndices[]')
        
            # print("I got remain index: ", remainIndex)
            # print("I got delete indices: ", delIndices)
        
            # Update the label lists of one of the image model in database 
            ukey = "airplanes/image_" + "{:04d}".format(int(remainIndex)) + ".jpg"
            imageup = ImageModel.objects.filter(img=ukey)
            if imageup:
                # Update the image set
                imageup.first().label.clear()
                
                for newlb in newlabels:
                    existlb = Label.objects.filter(name=newlb)
                    if existlb:
                        # Existing lb, only set is Taboo = True
                        existlb.update(isTaboo=True)
                        imageup.first().label.add(existlb.first())
                    else:
                        # Create new and add into the 
                        newlabel = Label.objects.create(name=newlb, isTaboo=True)
                        newlabel.save()
                        imageup.first().label.add(newlabel)
            else:
                print("wtf Error")

            # Remove the delIndices from the current list
            old_i_list = listArray.objects.get(phase='phase02')
            old_index = old_i_list.attrlist
            for di in delIndices:
                old_index.remove(int(di))
#           print("New index is: ", old_index)
            old_i_list.attrlist=old_index
            old_i_list.save()
        
            # If the length of the objects is less than 4, need to ask about "not same" vote from everyone once
            if len(old_index) <= 4:
                # Let the front-end show the "Not Same" Button
                showbutton = True
            
    # For GET, first check if phase 2 is finished or not created
    breaking = PhaseBreak.objects.filter(phase='phase02')

    if not breaking:
        print("generate phase break for phase02")
        breaking = PhaseBreak.objects.create(phase='phase02')
        breaking.save()
    else:
        print("exist, check if needed to stop")
        if breaking.first().stop:
            # save all the labels as attributes
            print("Stop here now")
            remainArray = listArray.objects.get(phase='phase02')
            for rI in remainArray.attrlist:
                key = "airplanes/image_" + "{:04d}".format(rI) + ".jpg"
                print("Set up attribute for image: ", key)
                attrimg = ImageModel.objects.get(img=key)
                labelsets = attrimg.label.all()
                for lbs in labelsets:
                    attribute = Attribute.objects.filter(word=lbs.name)
                    if not attribute:
                        attribute = Attribute.objects.create(word=lbs.name)
                        attribute.save()
                print("Done over here!")
            return render(request, 'over.html')
    # external files to get process the 
    # Get the index array model from database 
    
    print("Nothing should be here after stop")
    listarr = listArray.objects.filter(phase='phase02')
    # print("I got the existing index list: ", listarr.first().attrlist)
    
    if not listarr:
        # print("No list array exists, create a new one")
        listarr = rphase02(int(settings.NUMROUNDS))
        # print("listarr new is: ", listarr)
        # Create Model Instance and save
        p2list = listArray.objects.create(attrlist=listarr)
        p2list.save()
        indexlist = listarr
    else:
        indexlist = listarr.first().attrlist
    
    
    # Generate 4 random unique image number based on available entries
    sendArray = random.sample(indexlist, 4) if len(indexlist) > 4 else indexlist
    KEYS = map(KEY.format, sendArray)

    labels = list()

    for key in  KEYS:
        img = ImageModel.objects.get(img=key)
        label = img.label.all()

        if label.exists():
            labels.append(label)
        else:
            # else if there is nothing  
            pass
        
        # If the array list reaches the threhold (2), then set the breaking to be true.
        '''
            attribute = Attribute.objects.filter(word=attr).first()
            if attribute:
                # Not save the same name of the attribute twice
                pass
            else:
                attribute = Attribute.objects.create(word=attr)
                attribute.save()

        '''
    
    json_list = json.dumps(sendArray)
    # print("Phase 2 json list is: ", json_list)


                # print("this is new: ", attr)
    # In template use 1 for loop to print 3 label sets of 3 different images, and 1 more for loop to add elements into <li> element, change to phase02.html
    
    inst = Phase02_instruction.get_queryset(Phase02_instruction)
    instructions = list()
    if inst.exists():
        instructions = inst
    else: 
        instructions = ['none']
    return render(request, 'phase02.html', {'labels': labels, 'instructions': instructions, 'json_list': json_list, 'showbutton' : showbutton})


# View for phase3
@login_required
def phase03(request):

    
    attr = Attribute.objects.all()
    attributes = list()

    if attr.exists():
        attributes = attr
    else:
        # just send only none
        attributes = ['none']
    
    inst = Phase03_instruction.get_queryset(Phase03_instruction)
    instructions = list()
    if inst.exists():
        instructions = inst
    else: 
        instructions = ['none']
    
    # Update count
    if request.method == 'POST':
        dictionary = json.loads(request.POST['data[dict]'])
        for d in dictionary:
            # print("key: ", d, " value: ", dictionary[d])
            at = Attribute.objects.get(word=d)
            at.count += dictionary[d]
            at.save()
            
        return HttpResponse(None)
    else:
        return render(request, 'phase03.html', {'attributes': attributes, 'instructions': instructions})


