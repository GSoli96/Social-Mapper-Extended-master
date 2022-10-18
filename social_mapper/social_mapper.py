from __future__ import print_function
import shutil
import argparse
import http.cookiejar
import json
import math
import os
import shutil
import sys
import traceback
import urllib
from datetime import datetime
from shutil import copyfile
import json
import face_recognition
import numpy
import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.utils import encoding

from time import sleep
from modules import doubanfinder
from modules import facebookfinder
from modules import instagramfinder
from modules import linkedinfinder
from modules import pinterestfinder
from modules import twitterfinder
from modules import vkontaktefinder
from modules import weibofinder
from modules import modules_facesRecognition

assert sys.version_info >= (3,), "Only Python 3 is currently supported."

global linkedin_username
global linkedin_password
linkedin_username = "socialmappertest@libero.it" #jackslim089@tiscali.it
linkedin_password = "socialmapper97"

global facebook_username
global facebook_password
facebook_username = "social_test@libero.it" #"lucianapasqualazzi@yahoo.com"
facebook_password = "prova_SocialTest1" # "socialmapper97"

global twitter_username
global twitter_password
twitter_username = "PSocialmapper"
twitter_password = "socialmapper97"

global instagram_username
global instagram_password
instagram_username = "vexeco6853"#socialtest703"
instagram_password = "prova_SocialTest1" # "socialmapper97"

global google_username
global google_password
google_username = ""
google_password = ""

global vk_username
global vk_password
vk_username = "+393935126036"  # Can be mobile or email
vk_password = "socialmapper97"

global weibo_username
global weibo_password
weibo_username = ""  # Can be mobile
weibo_password = ""

global douban_username
global douban_password
douban_username = ""
douban_password = ""

global pinterest_username
global pinterest_password
pinterest_username = "socialmappertest@libero.it"
pinterest_password = "socialmapper97"

global typeFacesRecognition
typeFacesRecognition = 1 #metodo orginiale con Librearia: face_recognition  (Originale)           
#typeFacesRecognition = 2 #metodo Librearia: deepface (a Maggioranza)
 
# typeFacesRecognition = 3 #metodo Librearia: face_recognition - PIL - deepface  (face)  
# typeFacesRecognition = 4 #metodo Librearia: deepface (find)                                 
# typeFacesRecognition = 5 #metodo Librearia: deepface  (face a maggioranza) 

startTime = datetime.now()

# Classe che rappresenta l'effettia persona identificata tramite face recognition
class Person(object):
    first_name = ""
    last_name = ""
    full_name = ""
    person_image = ""
    person_imagelink = ""
    linkedin = ""
    linkedinimage = ""
    facebook = ""
    facebookimage = ""  # higher quality but needs authentication to access
    facebookcdnimage = ""  # lower quality but no authentication, used for HTML output
    twitter = ""
    twitterimage = ""
    instagram = ""
    instagramimage = ""
    vk = ""
    vkimage = ""
    weibo = ""
    weiboimage = ""
    douban = ""
    doubanimage = ""
    pinterest = ""
    pinterestimage = ""
    info_facebook = {"Work_and_Education": "", "Placed_Lives": "", "Contact_and_Basic_Info": "","Family_Relationships": "", "Detail_about": ""}
    info_linkedin = {"Cellulare": "", "Sito Web": "", "Email": "", "Compleanno": "", "Città": "","Impiego": "", "Indirizzo": "", "Messaggistica":"", "Biografia":"", "Formazione":"","Esperienze":""}
    info_vkontakte = {"Data di Nascita": "", "Città": "", "Studiato a": "", "Luogo di Nascita": "", "Lingue": "",
                      "Cellulare": "", "Telefono": "", "Skype": "", "College o università": "", "Stato": "",
                      "Scuola": "", "Gruppi": "", "Azienda": "", "Interesse": ""}
    info_instagram = {"Biografia": "", "Sito_Personale": ""}
    info_twitter = {"Città_twitter": "", "Sito_twitter": "", "Twitter_Biografia": ""}
    person_target_images_link = []
    numero_social = 0
    tipo_socials=[]

    def __init__(self, first_name, last_name, full_name, person_image,person_target_images_link):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.person_image = person_image
        self.person_target_images_link= person_target_images_link
        self.tipo_socials=[]
        self.numero_social = 0

# Classe che rappresenta le persone estrapolate con la semplice ricerca preliminare sul social
class PotentialPerson(object):
    full_name = ""
    profile_link = ""
    image_link = ""

    def __init__(self, full_name, profile_link, image_link):
        self.full_name = full_name
        self.profile_link = profile_link
        self.image_link = image_link

#
# Metodo che estrapola le infomazioni sul social Facebook
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_facebook(peoplelist):

    #login Facebook
    FacebookfinderObject = facebookfinder.Facebookfinder(showbrowser)
    FacebookfinderObject.doLogin(facebook_username, facebook_password)
    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        
        #controllo se esistono le directory utili
        create_removeDirectory()
        
        #per ogni immagine nella directory della persona
        for o in os.listdir('.\\Potential_target_image\\'+ person.full_name +'\\'):
            if o!=("Curriculum "+person.full_name+".pdf") and o!=("InfoRecognition.txt") and o!=(person.full_name+".jpg") and o!=(person.full_name+"_Li-Company.jpg") and (('.\\Potential_target_image\\'+ person.full_name +'\\'+o) not in person.person_target_images_link):
                #inserisco le immagini che dovranno essere controllate tramite face recognition
                person.person_target_images_link.append('.\\Potential_target_image\\'+ person.full_name +'\\'+o)
            else:
                continue

        if args.vv == True:
            print("Facebook Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rFacebook Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
       
        count = count + 1
        profilelist=[]

        
        if len(person.person_target_images_link) !=0:
            try:
                #effettua la ricerca di una persona sul social Facebook
                profilelist = FacebookfinderObject.getFacebookProfiles(person.first_name, person.last_name,
                                                                facebook_username, facebook_password)
                
            except Exception as e:
                #print(e)
                continue
        else:
            continue
        early_break = False
        updatedlist = []

        #creo path e titolo del file inerente i dati sul face recognition
        outputfilenameRecognition = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"
        titlestringRecognition = person.full_name + " - typeFacesRecognition: " + str(typeFacesRecognition)+" - threshold: "+ str(threshold)+", Social: Facebook\n"

        #scelgo il tipo di Face Recognition
        if(typeFacesRecognition==1):
            titlestringRecognition= titlestringRecognition + "Match,Distance, Link_Image, Link_SocialImage\n\n"
        elif(typeFacesRecognition==2):
             titlestringRecognition= titlestringRecognition + "Match, Distance, Threshold, Model, Link_Image, Link_SocialImage\n\n"
        # elif(typeFacesRecognition==3):
        #     titlestringRecognition= titlestringRecognition + "Match, Distance, Link_Image, Link_SocialImage\n\n"

        with open(outputfilenameRecognition, "a") as filewriterRecognition:
            filewriterRecognition.write(titlestringRecognition)

        #per ogni persona trovata sul social
        for profilelink, profilepic, distance, cdnpicture in profilelist:
            
            if early_break:
                break
            image_link = cdnpicture
            cookies = FacebookfinderObject.getCookies()
            
            if image_link:
                try:
                    
                    # Set fake user agent as Facebook blocks Python requests default user agent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'}
                    # Get target image using requests, providing Selenium cookies, and fake user agent
                    
                    response = requests.get(image_link, cookies=cookies, headers=headers, stream=True)
                    load_dir='.\\temp-targets\\'+person.full_name+'_FB.jpg'
                    
                    #scarico l'immagine di profilo sul dispositivo
                    with open(load_dir, 'wb') as out_file:
                        # Facebook images are sent content encoded so need to decode them
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, out_file)
                    del response

                    #confronto le immagini per capire se sia o meno la persona che sto cercando
                    results = typeRecognition(person, load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\',image_link)
                    
                    if results:
                        if args.mode == "fast":
                            person.facebook = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                            person.facebookimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                            person.facebookcdnimage = encoding.smart_str(cdnpicture, encoding='ascii',
                                                                            errors='ignore')
                                            
                            if args.vv == True:
                                print("\tMatch found: " + person.full_name)
                                print("\tFacebook: " + person.facebook)
                            
                            #estrepolo le informazioni circa la persona trovata
                            person.info_facebook = FacebookfinderObject.crawlerDataFacebook(facebook_username,facebook_password,person.facebook)
                                                                                                            
                            person.numero_social = person.numero_social + 1
                            person.tipo_socials.insert(0, 'fb')
                            early_break = True
                            
                            #scarico l'immagine di profilo sul dispositivo            
                            shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_FB.jpg')
                            
                            break
                        elif args.mode == "accurate":
                            person.facebook = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                            person.facebookimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                            person.facebookcdnimage = encoding.smart_str(cdnpicture, encoding='ascii',
                                                                            errors='ignore')
                            updatedlist.append([profilelink, image_link, 0.0, cdnpicture])

                            #estrepolo le informazioni circa la persona trovata
                            person.info_facebook = FacebookfinderObject.crawlerDataFacebook(facebook_username,facebook_password,
                                                                                                                person.facebook)                                             
                            person.numero_social = person.numero_social + 1
                            person.tipo_socials.insert(0, 'fb')

                            #scarico l'immagine di profilo sul dispositivo      
                            shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_FB.jpg')
                            break
                    else:
                        person.tipo_socials.insert(0, 'no_fb')
                        continue
                
                except Exception as e:
                    person.facebook = ""
                    person.facebookimage = ""
                    person.facebookcdnimage = ""
                    person.info_facebook = {"Work_and_Education": "", "Placed_Lives": "", "Contact_and_Basic_Info": "","Family_Relationships": "", "Detail_about": ""}
                    person.tipo_socials.insert(0, 'no_fb')
                    continue
            else:
                person.tipo_socials.insert(0, 'no_fb')
        # For accurate mode pull out largest distance and if it's bigger than the threshold then it's the most accurate result
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance, cdnpicture in updatedlist:
                if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                    if distance < highestdistance:
                        highestdistance = distance
                        bestprofilelink = profilelink
                        bestimagelink = image_link
                        bestcdnpicture = cdnpicture
            if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                if highestdistance < threshold:
                    person.facebook = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                    person.facebookimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                    person.facebookcdnimage = encoding.smart_str(bestcdnpicture, encoding='ascii', errors='ignore')
                    if args.vv == True:
                        print("\tMatch found: " + person.full_name)
                        print("\tFacebook: " + person.facebook)

                    #estrepolo le informazioni circa la persona trovata
                    person.info_facebook = FacebookfinderObject.crawlerDataFacebook(facebook_username, facebook_password,
                                                                                    person.facebook)
                    person.numero_social = person.numero_social + 1
                    person.tipo_socials.insert(0, 'fb')
                
    try:
        FacebookfinderObject.kill()
    except:
        print("Error Killing Facebook Selenium instance")
    
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Pinterest
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_pinterest(peoplelist):
    PinterestfinderObject = pinterestfinder.Pinterestfinder(showbrowser)
    PinterestfinderObject.doLogin(pinterest_username, pinterest_password)

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True:
            print("Pinterest Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rPinterest Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = PinterestfinderObject.getPinterestProfiles(person.first_name, person.last_name)
            except:
                continue
        else:
            continue

        early_break = False
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if numpy.all(result < threshold):
                                person.pinterest = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.pinterestimage = encoding.smart_str(image_link, encoding='ascii',
                                                                           errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tPinterest: " + person.pinterest)
                                person.numero_social = person.numero_social + 1
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if numpy.all(result < threshold):
                                updatedlist.append([profilelink, image_link, result])
                                person.numero_social = person.numero_social + 1
                except:
                    continue
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.pinterest = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.pinterestimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tPinterest: " + person.pinterest)
                person.numero_social = person.numero_social + 1

    try:
        PinterestfinderObject.kill()
    except:
        print("Error Killing Pinterest Selenium instance")
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Twitter
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_twitter(peoplelist):
    TwitterfinderObject = twitterfinder.Twitterfinder(showbrowser)
    TwitterfinderObject.doLogin(twitter_username, twitter_password)

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True:
            print("Twitter Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rTwitter Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = TwitterfinderObject.getTwitterProfiles(person.first_name, person.last_name)
            except:
                continue
        else:
            continue

        early_break = False
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            
            if early_break:
                break
            image_link = profilepic

            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.twitter = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.twitterimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tTwitter: " + person.twitter)
                                early_break = True
                                person.info_twitter = TwitterfinderObject.crawlerDataTwitter(twitter_username,
                                                                                             twitter_password,
                                                                                             person.twitter)
                                person.numero_social = person.numero_social + 1
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                updatedlist.append([profilelink, image_link, result])
                                person.info_twitter = TwitterfinderObject.crawlerDataTwitter(twitter_username,
                                                                                             twitter_password,
                                                                                             person.twitter)
                                person.numero_social = person.numero_social + 1
                except:
                    continue
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.twitter = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.twitterimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tTwitter: " + person.twitter)
                person.info_twitter = TwitterfinderObject.crawlerDataTwitter(twitter_username, twitter_password,
                                                                             person.twitter)
                person.numero_social = person.numero_social + 1

    try:
        TwitterfinderObject.kill()
    except:
        print("Error Killing Twitter Selenium instance")
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Instagram
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_instagram(peoplelist):

    #login
    InstagramfinderObject = instagramfinder.Instagramfinder(showbrowser)
    InstagramfinderObject.doLogin(instagram_username, instagram_password)

    count = 1
    ammount = len(peoplelist)
    
    outputDir_InfoIG = "SM-Results\\raccolta_info_imageIG\\"
            
    if not os.path.exists(outputDir_InfoIG):
        os.makedirs(outputDir_InfoIG)
    else:
        shutil.rmtree(outputDir_InfoIG)
        os.makedirs(outputDir_InfoIG)

    for person in peoplelist:
        #controllo se esistono le directory utili
        create_removeDirectory()

        #per ogni immagine nella directory della persona
        for o in os.listdir('.\\Potential_target_image\\'+ person.full_name +'\\'):
            if o!=("Curriculum "+person.full_name+".pdf") and o!=("InfoRecognition.txt") and o!=(person.full_name+".jpg") and o!=(person.full_name+"_Li-Company.jpg") and (('.\\Potential_target_image\\'+ person.full_name +'\\'+o) not in person.person_target_images_link):
               #inserisco le immagini che dovranno essere controllate tramite face recognition
                person.person_target_images_link.append('.\\Potential_target_image\\'+ person.full_name +'\\'+o)
            else:
                continue

        
        if args.vv == True:
            print("Instagram Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rInstagram Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        
        profilelist=[]
        if len(person.person_target_images_link) !=0:
            try: 
                #effettua la ricerca di una persona sul social Instagram
                profilelist = InstagramfinderObject.getInstagramProfiles(person.first_name, person.last_name,
                                                                          instagram_username, instagram_password)
            except Exception as e:
                #print(e)
                continue
        else:
            continue

        early_break = False
        updatedlist = []

        #creo path e titolo del file inerente i dati sul face recognition
        outputfilenameRecognition = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"
        titlestringRecognition = person.full_name + " - typeFacesRecognition: " + str(typeFacesRecognition)+" - threshold: "+ str(threshold)+", Social: Instagram\n"

        #scelgo il tipo di Face Recognition
        if(typeFacesRecognition==1):
            titlestringRecognition= titlestringRecognition + "Match,Distance, Link_Image, Link_SocialImage\n\n"
        elif(typeFacesRecognition==2):
             titlestringRecognition= titlestringRecognition + "Match, Distance, Threshold, Model, Link_Image, Link_SocialImage\n\n"
        # elif(typeFacesRecognition==3):
        #     titlestringRecognition= titlestringRecognition + "Match, Distance, Link_Image, Link_SocialImage\n\n"

        with open(outputfilenameRecognition, "a") as filewriterRecognition:
            filewriterRecognition.write(titlestringRecognition)

        #per ogni persona trovata sul social
        for profilelink, profilepic, verified in profilelist:
            if early_break:
                break
            image_link = profilepic

            if image_link:
                try:

                    #scarico l'immagine di profilo sul dispositivo
                    load_dir = '.\\temp-targets\\'+person.full_name+'_IG.jpg'
                    urllib.request.urlretrieve(image_link, load_dir)

                    #se il profilo è verificato
                    if(verified == False):

                        #confronto le immagini per capire se sia o meno la persona che sto cercando
                        results= typeRecognition(person, load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\',image_link)
                    
                        if results:
                            if args.mode == "fast":
                                person.instagram = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.instagramimage = encoding.smart_str(image_link, encoding='ascii',
                                                                                        errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tInstagram: " + person.instagram)

                                #estrepolo le informazioni circa la persona trovata
                                person.info_instagram = InstagramfinderObject.crawlerDataInstagram(instagram_username,instagram_password,person.instagram)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(1, 'ig')
                                early_break = True

                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_IG.jpg')
                                
                                #estrapolo tutti i post della persona
                                InstagramfinderObject.extract_Instagramimage(instagram_username,instagram_password,person)                                                                  
                                                    
                                       
                                break
                            elif args.mode == "accurate":
                                updatedlist.append([profilelink, image_link, 0.0])
                                person.instagram = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.instagramimage = encoding.smart_str(image_link, encoding='ascii',
                                                                                errors='ignore')

                                #estrepolo le informazioni circa la persona trovata
                                person.info_instagram = InstagramfinderObject.crawlerDataInstagram(instagram_username,
                                                                                                                instagram_password,
                                                                                                                person.instagram)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(1, 'ig')

                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_IG.jpg')
                                
                                #estrapolo tutti i post della persona
                                InstagramfinderObject.extract_Instagramimage(instagram_username,instagram_password,person)     
                                break
                                        
                    #se il profilo non è verificato
                    elif verified==True:
                        try:
                            #confronto le immagini per capire se sia o meno la persona che sto cercando
                            results= typeRecognition(person, load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\',image_link)
                    
                            if args.mode == "fast":
                                person.instagram = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.instagramimage = encoding.smart_str(image_link, encoding='ascii',
                                                                                errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tInstagram: " + person.instagram)
                                
                                #estrepolo le informazioni circa la persona trovata
                                person.info_instagram = InstagramfinderObject.crawlerDataInstagram(instagram_username,
                                                                                                        instagram_password,
                                                                                                        person.instagram)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(1, 'ig')
                                early_break = True

                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_IG.jpg')
                                
                                #estrapolo tutti i post della persona
                                InstagramfinderObject.extract_Instagramimage(instagram_username,instagram_password,person)             
                                break

                            elif args.mode == "accurate":
                                updatedlist.append([profilelink, image_link, 0.0])
                                person.instagram = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.instagramimage = encoding.smart_str(image_link, encoding='ascii',
                                                                                errors='ignore')
                                #estrepolo le informazioni circa la persona trovata
                                person.info_instagram = InstagramfinderObject.crawlerDataInstagram(instagram_username,
                                                                                                        instagram_password,
                                                                                                        person.instagram)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(1, 'ig')

                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_IG.jpg')
                                
                                #estrapolo tutti i post della persona
                                InstagramfinderObject.extract_Instagramimage(instagram_username,instagram_password,person)                                                                  
                                                
                                break

                        except Exception as e:
                            #traceback.print_exc(); print(e)
                            person.tipo_socials.insert(1, 'no_ig')
                            continue
                except Exception as e:
                   # traceback.print_exc(); print(e)
                    person.tipo_socials.insert(1, 'no_ig')
                    continue
                                 
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                    if distance < highestdistance:
                        highestdistance = distance
                        bestprofilelink = profilelink
                        bestimagelink = image_link
            if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                if highestdistance < threshold:
                    person.instagram = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                    person.instagramimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                    if args.vv == True:
                        print("\tMatch found: " + person.full_name)
                        print("\tInstagram: " + person.instagram)

                    #estrepolo le informazioni circa la persona trovata
                    person.info_instagram = InstagramfinderObject.crawlerDataInstagram(instagram_username,
                                                                                    instagram_password, person.instagram)
                    
                    #estrapolo tutti i post della persona
                    InstagramfinderObject.extract_Instagramimage(instagram_username,instagram_password,person)                                                                   
                                        
                    person.numero_social = person.numero_social + 1
                    person.tipo_socials.insert(1, 'ig')
                    
    try:
        InstagramfinderObject.kill()
    except:
        print("Error Killing Instagram Selenium instance")
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Linkedin
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_linkedin(peoplelist):
    #NO COMPANY
    if(args.format != "company"):
        #login
        LinkedinfinderObject = linkedinfinder.Linkedinfinder(showbrowser)
        LinkedinfinderObject.doLogin(linkedin_username, linkedin_password)

        count = 1
        ammount = len(peoplelist)
        for person in peoplelist:

            #controllo se esistono le directory utili
            create_removeDirectory()
            
            #per ogni immagine nella directory della persona
            for o in os.listdir('.\\Potential_target_image\\'+ person.full_name +'\\'):
                if o!=("Curriculum "+person.full_name+".pdf") and o!=("InfoRecognition.txt") and o!=(person.full_name+".jpg") and o!=(person.full_name+"_Li-Company.jpg") and (('.\\Potential_target_image\\'+ person.full_name +'\\'+o) not in person.person_target_images_link):
                    
                    #inserisco le immagini che dovranno essere controllate tramite face recognition
                    person.person_target_images_link.append('.\\Potential_target_image\\'+ person.full_name +'\\'+o)
                else:
                    continue

            if args.vv == True:
                print("LinkedIn Check %i/%i : %s" % (count, ammount, person.full_name))
            else:
                sys.stdout.write(
                    "\rLinkedIn Check %i/%i : %s                                " % (count, ammount, person.full_name))
                sys.stdout.flush()
            count = count + 1

            profilelist=[]
            if len(person.person_target_images_link) !=0:
                try:  
                    
                    #effettua la ricerca di una persona sul social Linkedin
                    profilelist = LinkedinfinderObject.getLinkedinProfiles(person.first_name, person.last_name,linkedin_username, linkedin_password)
                except:
                    continue
            else:
                continue


            early_break = False

            updatedlist = []

            #creo path e titolo del file inerente i dati sul face recognition
            outputfilenameRecognition = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"
            titlestringRecognition = person.full_name + " - typeFacesRecognition: " + str(typeFacesRecognition)+" - threshold: "+ str(threshold)+", Social: Linkedin\n"

            #scelgo il tipo di Face Recognition
            if(typeFacesRecognition==1):
                titlestringRecognition= titlestringRecognition + "Match,Distance, Link_Image, Link_SocialImage\n\n"
            elif(typeFacesRecognition==2):
                titlestringRecognition= titlestringRecognition + "Match, Distance, Threshold, Model, Link_Image, Link_SocialImage\n\n"
            # elif(typeFacesRecognition==3):
            #     titlestringRecognition= titlestringRecognition + "Match, Distance, Link_Image, Link_SocialImage\n\n"

            with open(outputfilenameRecognition, "a") as filewriterRecognition:
                filewriterRecognition.write(titlestringRecognition)

            #per ogni persona trovata sul social
            for profilelink, profilepic, distance in profilelist:
                if early_break:
                    break
                image_link = profilepic
                if image_link:
                    try:
                        
                        #scarico l'immagine di profilo sul dispositivo
                        load_dir = '.\\temp-targets\\'+person.full_name+'_i.jpg'
                        urllib.request.urlretrieve(image_link, load_dir)

                        #confronto le immagini per capire se sia o meno la persona che sto cercando
                        results= typeRecognition(person, load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\',image_link)

                        if results:
                            if args.mode == "fast":
                                person.linkedin = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.linkedinimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tLinkedIn: " + person.linkedin)

                                #estrepolo le informazioni circa la persona trovata
                                person.info_linkedin = LinkedinfinderObject.crawlerDataLinkedin(linkedin_username,linkedin_password,
                                                                                                        person.linkedin, person.full_name)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(2, 'li')
                                early_break = True
                                
                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_Li.jpg')
                                        
                                break
                            elif args.mode == "accurate":
                                person.linkedin = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.linkedinimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                updatedlist.append([profilelink, image_link, 0.0])

                                #estrepolo le informazioni circa la persona trovata
                                person.info_linkedin = LinkedinfinderObject.crawlerDataLinkedin(linkedin_username,linkedin_password,
                                                                                                        person.linkedin,person.full_name)
                                person.numero_social = person.numero_social + 1
                                person.tipo_socials.insert(2, 'li')
                                
                                #scarico l'immagine di profilo sul dispositivo
                                shutil.copyfile(load_dir, '.\\Potential_target_image\\'+ person.full_name +'\\'+person.full_name+'_Li.jpg')
                                break

                    except Exception as e:
                        person.tipo_socials.insert(2, 'no_li')
                        # print(e)
                        continue

            if args.mode == "accurate":
                highestdistance = 1.0
                bestprofilelink = ""
                bestimagelink = ""
                for profilelink, image_link, distance in updatedlist:
                    if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                        if distance < highestdistance:
                            highestdistance = distance
                            bestprofilelink = profilelink
                            bestimagelink = image_link
                if(typeFacesRecognition!=2 and typeFacesRecognition!=4 and typeFacesRecognition !=5):
                    if highestdistance < threshold:
                        person.linkedin = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                        person.linkedinimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                        if args.vv == True:
                            print("\tMatch found: " + person.full_name)
                            print("\tLinkedIn: " + person.linkedin)

                        #estrepolo le informazioni circa la persona trovata
                        person.info_linkedin = LinkedinfinderObject.crawlerDataLinkedin(linkedin_username, linkedin_password,
                                                                                        person.linkedin,person.full_name)
                        person.numero_social = person.numero_social + 1
                        person.tipo_socials.insert(2, 'li')
                    

        try:
            LinkedinfinderObject.kill()
        except:
            print("Error Killing LinkedIn Selenium instance")
        return peoplelist


    #COMPANY  
    elif(args.format == "company"):

        #login
        LinkedinfinderObject = linkedinfinder.Linkedinfinder(showbrowser)
        LinkedinfinderObject.doLogin(linkedin_username, linkedin_password)

        count_company = 1
        ammount_company = len(peoplelist)
        for person in peoplelist:
            try:

                #controllo se esistono le directory utili
                create_removeDirectory()

                #per ogni immagine nella directory della persona
                for o in os.listdir('.\\Potential_target_image\\'+ person.full_name +'\\'):
                    if o!=("Curriculum "+person.full_name+".pdf") and o!=("InfoRecognition.txt") and o!=(person.full_name+".jpg") and o!=(person.full_name+"_Li-Company.jpg") and (('.\\Potential_target_image\\'+ person.full_name +'\\'+o) not in person.person_target_images_link):
                        
                        #inserisco le immagini che dovranno essere controllate tramite face recognition
                        person.person_target_images_link.append('.\\Potential_target_image\\'+ person.full_name +'\\'+o)
                    else:
                        continue

                if args.vv == True:
                    print("LinkedIn Check %i/%i : %s" % (count_company, ammount_company, person.full_name))
                else:
                    sys.stdout.write(
                    "\rLinkedIn Check %i/%i : %s                                " % (count_company, ammount_company, person.full_name))
                    sys.stdout.flush()
                count_company = count_company + 1

                profilelist=[]
                if len(person.person_target_images_link) !=0:
                    try:  
                        
                        #effettua la ricerca di una persona sul social Linkedin
                        profilelist = LinkedinfinderObject.getLinkedinProfiles(person.first_name, person.last_name,linkedin_username, linkedin_password)
                    except:
                        continue
                else:
                    continue

                person.linkedin = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                person.linkedinimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tLinkedIn: " + person.linkedin)

                #estrepolo le informazioni circa la persona trovata
                person.info_linkedin = LinkedinfinderObject.crawlerDataLinkedin(linkedin_username,linkedin_password,person.linkedin,person.full_name)
                person.numero_social = person.numero_social + 1
                person.tipo_socials.insert(2, 'li')
                break
            except Exception as e:
                person.tipo_socials.insert(2, 'no_li')
                # print(e)
                continue
                    
        try:
            LinkedinfinderObject.kill()
        except:
            print("Error Killing LinkedIn Selenium instance")          
        
        return peoplelist


#
# Metodo che estrapola le infomazioni sul social Vkontakte
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_vkontakte(peoplelist):
    VkontaktefinderObject = vkontaktefinder.Vkontaktefinder(showbrowser)
    VkontaktefinderObject.doLogin(vk_username, vk_password)

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True:
            print("VKontakte Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rVKontakte Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = VkontaktefinderObject.getVkontakteProfiles(person.first_name, person.last_name)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.vk = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.vkimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tVkontakte: " + person.vk)
                                person.info_vkontakte = VkontaktefinderObject.crawlerDataVkontackte(vk_username,
                                                                                                    vk_password,
                                                                                                    person.vk)
                                person.numero_social = person.numero_social + 1
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                                person.info_vkontakte = VkontaktefinderObject.crawlerDataVkontackte(vk_username,
                                                                                                    vk_password,
                                                                                                    person.vk)
                                person.numero_social = person.numero_social + 1
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.vk = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.vkimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tVkontakte: " + person.vk)
                person.info_vkontakte = VkontaktefinderObject.crawlerDataVkontackte(vk_username, vk_password,
                                                                                    person.vk)
                person.numero_social = person.numero_social + 1

    try:
        VkontaktefinderObject.kill()
    except:
        print("Error Killing VKontakte Selenium instance")
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Weibo
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_weibo(peoplelist):
    WeibofinderObject = weibofinder.Weibofinder(showbrowser)
    WeibofinderObject.doLogin(weibo_username, weibo_password)

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True:
            print("Weibo Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rWeibo Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = WeibofinderObject.getWeiboProfiles(person.first_name, person.last_name)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.weibo = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.weiboimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tWeibo: " + person.weibo)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.weibo = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.weiboimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tWeibo: " + person.weibo)

    try:
        WeibofinderObject.kill()
    except:
        print("Error Killing Weibo Selenium instance")
    return peoplelist

#
# Metodo che estrapola le infomazioni sul social Douban
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
def fill_douban(peoplelist):
    DoubanfinderObject = doubanfinder.Doubanfinder(showbrowser)
    DoubanfinderObject.doLogin(douban_username, douban_password)

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True:
            print("Douban Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rDouban Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = DoubanfinderObject.getDoubanProfiles(person.first_name, person.last_name)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    #COPIA LA FOTO DELLA PERSONA DA INTERNET E LA METTE IN potential target
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.douban = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.doubanimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tDouban: " + person.douban)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.douban = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.doubanimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tDouban: " + person.douban)

    try:
        DoubanfinderObject.kill()
    except:
        print("Error Killing Douban Selenium instance")
    return peoplelist


# Login function for LinkedIn for company browsing (Credits to LinkedInt from MDSec)
def login():
    cookie_filename = "cookies.txt"
    cookiejar = http.cookiejar.MozillaCookieJar(cookie_filename)
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler(), urllib.request.HTTPHandler(debuglevel=0),
                                         urllib.request.HTTPSHandler(debuglevel=0),
                                         urllib.request.HTTPCookieProcessor(cookiejar))

    page = loadPage(opener, "https://www.linkedin.com/uas/login").decode('utf-8')
    parse = BeautifulSoup(page, "html.parser")
    csrf = ""
    for link in parse.find_all('input'):
        name = link.get('name')
        if name == 'loginCsrfParam':
            csrf = link.get('value')
    login_data = urllib.parse.urlencode(
        {'session_key': linkedin_username, 'session_password': linkedin_password, 'loginCsrfParam': csrf})
    page = loadPage(opener, "https://www.linkedin.com/checkpoint/lg/login-submit", login_data).decode('utf-8')

    parse = BeautifulSoup(page, "html.parser")
    cookie = ""
    try:
        cookie = cookiejar._cookies['.www.linkedin.com']['/']['li_at'].value
    except:
        print("Error logging in! Try changing language on social networks or verifying login data.")
        print("If a capcha is required to login (due to excessive attempts) it will keep failing, try using a VPN or running with the -s flag to show the browser, where you can manually solve the capcha.")
        sys.exit(0)
    cookiejar.save()
    os.remove(cookie_filename)
    return cookie

#
# Metodo che crea la sessione su Linkedin nel caso di ricerca per compagnia
#
# @return cookies Lista dei cookies presenti
#
def authenticate():
    try:
        a = login()
        session = a
        if len(session) == 0:
            sys.exit("[!] Unable to login to LinkedIn.com")
        print(("[*] Obtained new session: %s" % session))
        cookies = dict(li_at=session)
    except Exception as e:
        sys.exit("[!] Could not authenticate to LinkedIn. %s" % e)
    return cookies

#
# Metodo che controlla se ogni directory utile esiste
#
def create_removeDirectory():
    try:
        #directory temporanea per il salvataggio delle foto dei profili social
        if not os.path.exists('temp-targets'):
                    os.makedirs('temp-targets')
        else:
            shutil.rmtree('temp-targets')
            os.makedirs('temp-targets')

        #directory temporanea utile per la face recognition 
        if not os.path.exists('temp-targets\\Original_face'):
            os.makedirs('temp-targets\\Original_face')

        if not os.path.exists('temp-targets\\Profile_face'):
                os.makedirs('temp-targets\\Profile_face')
    except:
        print("Error Directory")
        pass


#
# Metodo che crea la sessione su Linkedin nel caso di ricerca per compagnia
#
# @param client Client HTTP su cui lavorare
# @param url Stringa che rappresenta l'url della pagina da caricare
# @return byteArray pagina caricata
#
def loadPage(client, url, data=None):
    try:
        if data is not None:
            try:
                response = client.open(url, data.encode("utf-8"))
            except:
                print("[!] Cannot load main LinkedIn GET page")
        else:
            try:
                response = client.open(url)
            except:
                print("[!] Cannot load main LinkedIn POST page")
        emptybyte = bytearray()
        return emptybyte.join(response.readlines())
    except:
        traceback.print_exc()
        sys.exit(0)


# Setup Argument parser to print help and lock down options
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Social Mapper by Jacob Wilkin (Greenwolf)',
    usage='%(prog)s -f <format> -i <input> -m <mode> -t <threshold> <options>')
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 0.1.0 : Social Mapper by Greenwolf (Github Link Here)')
parser.add_argument('-vv', '--verbose', action='store_true', dest='vv', help='Verbose Mode')
parser.add_argument('-f', '--format', action='store', dest='format', required=True,
                    choices=set(("csv", "imagefolder", "company", "socialmapper")),
                    help='Specify if the input file is either a \'company\',a \'CSV\',a \'imagefolder\' or a Social Mapper HTML file to resume')
parser.add_argument('-i', '--input', action='store', dest='input', required=True,
                    help='The name of the CSV file, input folder or company name to use as input')
parser.add_argument('-m', '--mode', action='store', dest='mode', required=True, choices=set(("accurate", "fast")),
                    help='Selects the mode either accurate or fast, fast will report the first match over the threshold while accurate will check for the highest match over the threshold')
parser.add_argument('-t', '--threshold', action='store', dest='thresholdinput', required=False,
                    choices=set(("loose", "standard", "strict", "superstrict")),
                    help='The strictness level for image matching, default is standard but can be specified to loose, standard, strict or superstrict')
parser.add_argument('-e', '--email', action='store', dest='email', required=False,
                    help='Provide an email format to trigger phishing list generation output, should follow a convention such as "<first><last><f><l>@domain.com"')
parser.add_argument('-cid', '--companyid', action='store', dest='companyid', required=False,
                    help='Provide an optional company id, for use with \'-f company\' only')

parser.add_argument('-s', '--showbrowser', action='store_true', dest='showbrowser',
                    help='If flag is set then browser will be visible')

parser.add_argument('-a', '--all', action='store_true', dest='a', help='Flag to check all social media sites')
parser.add_argument('-fb', '--facebook', action='store_true', dest='fb', help='Flag to check Facebook')
parser.add_argument('-pin', '--pinterest', action='store_true', dest='pin', help='Flag to check Pinterest')
parser.add_argument('-tw', '--twitter', action='store_true', dest='tw', help='Flag to check Twitter')
parser.add_argument('-ig', '--instagram', action='store_true', dest='ig', help='Flag to check Instagram')

# parser.add_argument('-img', '--instagram_image', action='store_true', dest='img', help='Flag to check Instagram Image Post')
parser.add_argument('-li', '--linkedin', action='store_true', dest='li',
                    help='Flag to check LinkedIn - Automatic with \'company\' input type')
parser.add_argument('-vk', '--vkontakte', action='store_true', dest='vk',
                    help='Flag to check the Russian VK VKontakte Site')
parser.add_argument('-wb', '--weibo', action='store_true', dest='wb', help='Flag to check the Chinese Weibo Site')
parser.add_argument('-db', '--douban', action='store_true', dest='db', help='Flag to check the Chinese Douban Site')

args = parser.parse_args()

if not (args.a or args.fb or args.tw or args.pin or args.ig or args.li or args.vk or args.wb or args.db):
    parser.error(
        'No sites specified requested, add -a for all, or a combination of the sites you want to check using a mix of -fb -tw -ig -li -pin -vk -db -wb')

# Set up face matching threshold
threshold = 0.60
try:
    if args.thresholdinput == "superstrict":
        threshold = 0.40
    if args.thresholdinput == "strict":
        threshold = 0.50
    if args.thresholdinput == "standard":
        threshold = 0.60
    if args.thresholdinput == "loose":
        threshold = 0.70
except:
    pass

if args.showbrowser:
    showbrowser = True
else:
    showbrowser = False

exit = True
# remove targets dir for remaking
if os.path.exists('temp-targets'):
    shutil.rmtree('temp-targets')
# people list to hold people in memory
peoplelist = []

# Fill people list from document with just name + image link
if args.format == "csv":
    exit = False

    if not os.path.exists('temp-targets'):
        os.makedirs('temp-targets')
    dataframe = pd.read_csv(args.input, ",", usecols=['name', 'url'])

    for index in range(len(dataframe)):
        try:
            full_name = dataframe['name'][index]
            person_image = dataframe['url'][index]
            full_name = encoding.smart_str(full_name, encoding='ascii', errors='ignore')
            person_image = encoding.smart_str(person_image, encoding='ascii', errors='ignore')

            first_name = full_name.split(" ")[0]
            last_name = full_name.split(" ")[1]
            person_target_images_link=[person_image]
            person = Person(first_name, last_name, full_name, "./Input-Examples/imagefolder/" + full_name + ".jpg",person_target_images_link)
            person.person_imagelink = person_image
            peoplelist.append(person)
        except Exception as e:
            print("Error getting image or creating person structure, skipping:" + full_name)
# remove this when fixed downloading
# sys.exit(1)

# Parse image folder full of images and names into social_mapper
if args.format == "imagefolder":
    if not args.input.endswith("/"):
        args.input = args.input + "/"
    exit = False
    
    dir_potential_target= ".\\Potential_target_image"
            
    if not os.path.exists(dir_potential_target):
            os.makedirs(dir_potential_target)
    else:
        shutil.rmtree(dir_potential_target)
        os.makedirs(dir_potential_target)

    if not os.path.exists("SM-Results"):
        os.makedirs("SM-Results")

    if not os.path.exists("SM-Results\\raccolta_info_imageIG"):
        os.makedirs("SM-Results\\raccolta_info_imageIG")



        

    for filename in os.listdir(args.input):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            full_name = filename.split(".")[0]
            first_name = full_name.split(" ")[0]
            
            try:
                last_name = full_name.replace(first_name + " ", "")
            except:
                last_name = ""
            first_name = encoding.smart_str(first_name, encoding='ascii', errors='ignore')
            last_name = encoding.smart_str(last_name, encoding='ascii', errors='ignore')
            full_name = encoding.smart_str(full_name, encoding='ascii', errors='ignore')
            
            
            person_dir= ".\\Potential_target_image\\" + full_name+"\\"
            try:
                os.makedirs(person_dir)
            except:
                continue

           

            original = ('.\\imagefolder\\'+ filename)
            target =('.\\Potential_target_image\\' + full_name+'\\'+filename)
            
            shutil.copyfile(original, target)
            link_dir= ['.\\Potential_target_image\\' + full_name+'\\'+filename]
            person = Person(first_name, last_name, full_name,  args.input + filename, link_dir)
            person.person_imagelink = args.input + filename
            peoplelist.append(person)


# Get targets from LinkedIn company search
if args.format == "company":
    exit = False
    
    if os.path.exists("Potential_target_image"):
        shutil.rmtree("Potential_target_image")
        os.makedirs("Potential_target_image")
    elif not os.path.exists("Potential_target_image"):
        os.makedirs("Potential_target_image")

    if not os.path.exists("SM-Results"):
        os.makedirs("SM-Results")
    
    if os.path.exists("SM-Results\\raccolta_info_imageIG"):
        shutil.rmtree("SM-Results\\raccolta_info_imageIG")
        os.makedirs("SM-Results\\raccolta_info_imageIG")

    if not os.path.exists('temp-targets'):
        os.makedirs('temp-targets')

    cookies = authenticate()  # perform authentication
    companyid = 0
    if args.companyid is not None:  # Don't find company id, use provided id from -cid or --companyid flag
        print("Using supplied company Id: %s" % args.companyid)
        companyid = args.companyid
    else:
        # code to get company ID based on name
        companyid = 0
        url = "https://www.linkedin.com/voyager/api/typeahead/hits?q=blended&query=%s" % args.input
        headers = {'Csrf-Token': 'ajax:0397788525211216808', 'X-RestLi-Protocol-Version': '2.0.0'}
        cookies['JSESSIONID'] = 'ajax:0397788525211216808'
        r = requests.get(url, cookies=cookies, headers=headers)
        content = json.loads(r.text)
        firstID = 0
        for i in range(0, len(content['elements'])):
            try:
                companyid = content['elements'][i]['hitInfo']['com.linkedin.voyager.typeahead.TypeaheadCompany']['id']
                if firstID == 0:
                    firstID = companyid
                print("[Notice] Found company ID: %s" % companyid)
            except:
                continue
        companyid = firstID
        if companyid == 0:
            print("[WARNING] No valid company ID found in auto, please restart and find your own")
            sys.exit(1)
    print("[*] Using company ID: %s" % companyid)
    
    sleep(2)
    url = "https://www.linkedin.com/voyager/api/search/cluster?count=10&guides=List(v->PEOPLE,facetCurrentCompany->%s)&origin=OTHER&q=guided&start=0" % (
        companyid)
    headers = {'Csrf-Token': 'ajax:0397788525211216808', 'X-RestLi-Protocol-Version': '2.0.0'}
    cookies['JSESSIONID'] = 'ajax:0397788525211216808'
    r = requests.get(url, cookies=cookies, headers=headers)
    content = json.loads(r.text)
    try:
        data_total = content['elements'][0]['total']
    except IndexError:
        print("Company has no people listed, nothing to match against other Social Networks!")
        sys.exit(0)

    # Calculate pages off final results at 10 results/page
    pages = math.ceil(data_total / 10)
    if pages == 0:
        pages = 1
    if data_total % 10 == 0:
        # Because we count 0... Subtract a page if there are no left over results on the last page
        pages = pages - 1
    if pages == 0:
        print("[!] Try to use quotes in the search name")
        sys.exit(0)

    print("[*] %i Results Found" % data_total)
    if data_total > 1000:
        pages = 100
        print("[*] LinkedIn only allows 1000 results. Refine keywords to capture all data")
    print("[*] Fetching %i Pages" % pages)
    print()
    companyname = args.input.strip("\"")
    for p in range(pages):
        url = "https://www.linkedin.com/voyager/api/search/cluster?count=10&guides=List(v->PEOPLE,facetCurrentCompany->%s)&origin=OTHER&q=guided&start=%i" % (
        companyid, p * 10)
        r = requests.get(url, cookies=cookies, headers=headers)
        content = r.text.encode('UTF-8')
        content = json.loads(content)
        # print "[*] Fetching page %i with %i results for %s" % ((p),len(content['elements'][0]['elements']),companyname)
        sys.stdout.write("\r[*] Fetching page %i/%i with %i results for %s" % (
        (p), pages, len(content['elements'][0]['elements']), companyname))
        sys.stdout.flush()
        # code to get users, for each user with a picture create a person
        for c in content['elements'][0]['elements']:
            if 'com.linkedin.voyager.search.SearchProfile' in c['hitInfo'] and \
                c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['headless'] == False:
                try:

                    # get the link to profile pic, link to LinkedIn profile page, and their full name
                    # person_image = "https://media.licdn.com/mpr/mpr/shrinknp_400_400%s" % c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']['picture']['com.linkedin.voyager.common.MediaProcessorImage']['id']
                    first_name = c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']['firstName']
                    first_name = encoding.smart_str(first_name, encoding='ascii', errors='ignore')
                    first_name = first_name.lower()
                    last_name = c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']['lastName']
                    last_name = encoding.smart_str(last_name, encoding='ascii', errors='ignore')
                    last_name = last_name.lower()
                    # Around 30% of people keep putting Certs in last name, so strip these out.
                    tmp_1 = last_name.split(' ', 1)[0]
                    tmp_2 = last_name.split(' ', 1)[1]
                   

                    list_p = [",", "mba", "-", "-"]
                    for p in list_p:
                        tmp_1 = tmp_1.replace(p , "")
                        tmp_2 = tmp_2.replace(p , "")

                    last_name = tmp_1 +" "+ tmp_2

                    full_name = first_name.capitalize() + " " + last_name.capitalize()
                    
                    full_name= ((full_name).encode('ascii', 'ignore').decode('ascii'))+''
                    sign =["(", ")", ".", ",", "-", "_","]", "[", "'"]
                    
                    first_name = ((first_name).encode('ascii', 'ignore').decode('ascii'))+''
                    last_name =((last_name).encode('ascii', 'ignore').decode('ascii'))+''
                    
                    for s in sign:
                        full_name = full_name.replace(s, "")
                        first_name = first_name.replace(s, "")
                        last_name = last_name.replace(s, "")
                        
                    dir_potential_target_image= '.\\Potential_target_image\\'+ full_name
            
                    if not os.path.exists(dir_potential_target_image):
                            os.makedirs(dir_potential_target_image) 
            

                    if not os.path.exists("SM-Results\\raccolta_info_imageIG\\"+full_name):
                        os.makedirs("SM-Results\\raccolta_info_imageIG\\"+full_name) 
                    
                    rooturl = c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']['picture'][
                        'com.linkedin.common.VectorImage']['rootUrl']
                    artifact = c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']['picture'][
                        'com.linkedin.common.VectorImage']['artifacts'][3]['fileIdentifyingUrlPathSegment']
                    person_image = rooturl + artifact
                    
                    person_image = encoding.smart_str(person_image, encoding='ascii', errors='ignore')
                                        
                    linkedin = "https://www.linkedin.com/in/%s" % \
                               c['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile'][
                                   'publicIdentifier']      
                    linkedin = encoding.smart_str(linkedin, encoding='ascii', errors='ignore')
                    #urllib.request.urlretrieve(person_image, "temp-targets/" + full_name + ".jpg")

                    load_dir = '.\\Potential_target_image\\'+ full_name +'\\'+full_name+'_Li-Company.jpg'
                    urllib.request.urlretrieve(person_image, load_dir)
                    link_dir= [load_dir]
                    person = Person(first_name, last_name, full_name, load_dir, link_dir)
                    person.person_imagelink = person_image
                    person.linkedin = linkedin
                    person.linkedinimage = person_image
                    
                    peoplelist.append(person)
                   
                except Exception as e:
                    # This triggers when a profile doesn't have an image associated with it
                    continue

    peoplelist = fill_linkedin(peoplelist)    


# To continue a Social Mapper run for additional sites.
if args.format == "socialmapper":
    if args.a == True:
        print(
            "This option is for adding additional sites to a Social Mapper report\nFeed in a Social Mapper HTML file that's only been partially run, for example:\nFirst run (LinkedIn, Facebook, Twitter): python social_mapper -f company -i \"SpiderLabs\" -m fast -t standard -li -fb -tw\n Second run (adding Instagram and Google Plus): python social_mapper -f socialmapper -i SpiderLabs-social-mapper.html -m fast -t standard -ig -gp")
        sys.exit(1)
    exit = False
    try:
        os.remove('backup.html')
    except OSError:
        pass
    if not os.path.exists('temp-targets'):
        os.makedirs('temp-targets')
    copyfile(args.input, 'SM-Results/backup.html')
    print("Backup of original report created: 'SM-Results/backup.html'")

    f = open(args.input)
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    tbodylist = soup.findAll("tbody")
    for personhtml in tbodylist:
        person_image = encoding.smart_str(personhtml.findAll("td")[0].string, encoding='ascii',
                                          errors='ignore').replace(";", "")
        full_name = encoding.smart_str(personhtml.findAll("td")[1].string, encoding='ascii', errors='ignore')
        first_name = full_name.split(" ")[0]
        last_name = full_name.split(" ", 1)[1]
        urllib.request.urlretrieve(person_image, "temp-targets/" + full_name + ".jpg")

        link_dir= ["temp-targets/" + full_name + ".jpg"]
        person = Person(first_name, last_name, full_name, "temp-targets/" + full_name + ".jpg",link_dir)
        person.person_imagelink = person_image
        person.linkedin = encoding.smart_str(personhtml.findAll("td")[2].find("a")['href'], encoding='ascii',
                                             errors='ignore').replace(";", "")
        person.linkedinimage = encoding.smart_str(personhtml.findAll("td")[2].find("img")['src'], encoding='ascii',
                                                  errors='ignore').replace(";", "")
        person.facebook = encoding.smart_str(personhtml.findAll("td")[3].find("a")['href'], encoding='ascii',
                                             errors='ignore').replace(";", "")
        person.facebookimage = encoding.smart_str(personhtml.findAll("td")[3].find("img")['src'], encoding='ascii',
                                                  errors='ignore').replace(";", "")
        person.facebookcdnimage = encoding.smart_str(personhtml.findAll("td")[3].find("img")['src'], encoding='ascii',
                                                     errors='ignore').replace(";", "")
        person.twitter = encoding.smart_str(personhtml.findAll("td")[4].find("a")['href'], encoding='ascii',
                                            errors='ignore').replace(";", "")
        person.twitterimage = encoding.smart_str(personhtml.findAll("td")[4].find("img")['src'], encoding='ascii',
                                                 errors='ignore').replace(";", "")
        person.pinterest = encoding.smart_str(personhtml.findAll("td")[4].find("a")['href'], encoding='ascii',
                                              errors='ignore').replace(";", "")
        person.pinterestimage = encoding.smart_str(personhtml.findAll("td")[4].find("img")['src'], encoding='ascii',
                                                   errors='ignore').replace(";", "")
        person.instagram = encoding.smart_str(personhtml.findAll("td")[5].find("a")['href'], encoding='ascii',
                                              errors='ignore').replace(";", "")
        person.instagramimage = encoding.smart_str(personhtml.findAll("td")[5].find("img")['src'], encoding='ascii',
                                                   errors='ignore').replace(";", "")
        person.vk = encoding.smart_str(personhtml.findAll("td")[7].find("a")['href'], encoding='ascii',
                                       errors='ignore').replace(";", "")
        person.vkimage = encoding.smart_str(personhtml.findAll("td")[7].find("img")['src'], encoding='ascii',
                                            errors='ignore').replace(";", "")
        person.weibo = encoding.smart_str(personhtml.findAll("td")[8].find("a")['href'], encoding='ascii',
                                          errors='ignore').replace(";", "")
        person.weiboimage = encoding.smart_str(personhtml.findAll("td")[8].find("img")['src'], encoding='ascii',
                                               errors='ignore').replace(";", "")
        person.douban = encoding.smart_str(personhtml.findAll("td")[9].find("a")['href'], encoding='ascii',
                                           errors='ignore').replace(";", "")
        person.doubanimage = encoding.smart_str(personhtml.findAll("td")[9].find("img")['src'], encoding='ascii',
                                                errors='ignore').replace(";", "")
        peoplelist.append(person)

if exit:
    print("Input Error, check options relating to format and input")
    sys.exit(1)

#
# Metodo contenente i tipi di face recogntion disponibili
#
# @param person Persona da identificare tramite Face_Recognition
# @param socia_img Stringa che rappresenta la foto della persona sui social trovata 
# @param path Stringa che rappresenta il percorso in cui sono posizionate le immagini utili
# @param image_link Stringa legata all'immagine di profilo della persona ricercata
#
# @return Bool Valore booleano che identifica il risultato del processo di face recognition
#
def typeRecognition(person,social_img, path,image_link):
    try:
        
        module_facesRecognition = modules_facesRecognition.modules_facesRecognition()

        if typeFacesRecognition == 1:
            #metodo orginiale con Librearia: face_recognition
            #Calcola la distanza tra due facce nelle foto
            return module_facesRecognition.facesDistance_FR(social_img, threshold, person,image_link)
             

        elif typeFacesRecognition == 2:
            #metodo Librearia: deepface
            # effettua un conftronto a maggioranza
            return module_facesRecognition.deepFace_majority(social_img,person,image_link)


        elif typeFacesRecognition == 3: 
            #metodo Librearia: face_recognition - PIL - deepface 
            return module_facesRecognition.cut_Recognition(social_img, threshold,person,image_link)
            

        elif typeFacesRecognition == 4:
            #metodo Librearia: deepface
            #Calcola la distanza tra due facce nelle foto
            return module_facesRecognition.face_recognition(path,threshold,person,image_link)


        elif typeFacesRecognition == 5:
            #metodo Librearia: deepface
            #Calcola la distanza tra due facce nelle foto
            return module_facesRecognition.face_majority(social_img, threshold,person,image_link)


    except Exception as e:
        #traceback.print_exc()
        #print(e)
        return False


#
# Metodo che consente di rieseguire l'agoritmo per tutti quei social in cui non si è riusciti ad avere risultati
#
# @param peoplelist lista delle persone da ricercare
#
# @return peoplelist lista delle persone da ricercare aggiornata
#
# def re_check(peoplelist):
    
#     print("\n[+] Socials Recheck [+]\n")
#     for person in peoplelist:
#         rc_peoplelist=[person]

#         if 'no_ig' in person.tipo_socials:
#             if not (instagram_username == "" or instagram_password == ""):
                
#                 rc_peoplelist = fill_instagram(rc_peoplelist)
                
#                 person.instagram = rc_peoplelist[0].instagram
#                 person.instagramimage = rc_peoplelist[0].instagramimage
#                 person.info_instagram = rc_peoplelist[0].info_instagram
#                 person.numero_social = rc_peoplelist[0].numero_social
#                 person.tipo_socials = rc_peoplelist[0].tipo_socials
#             else:
#                 print("Please provide Instagram Login Credentials in the social_mapper.py file")
#         elif 'no_fb' in person.tipo_socials:
#             if not (facebook_username == "" or facebook_password == ""):
#                 try:
#                     rc_peoplelist = fill_facebook(rc_peoplelist)
                    
#                     person.facebook = rc_peoplelist[0].facebook
#                     person.facebookimage = rc_peoplelist[0].facebookimage
#                     person.facebookcdnimage = rc_peoplelist[0].facebookcdnimage
#                     person.info_facebook = rc_peoplelist[0].info_facebook
#                     person.numero_social = rc_peoplelist[0].numero_social
#                     person.tipo_socials = rc_peoplelist[0].tipo_socials
#                 except Exception as e:
#                     print("[-] Error Filling out Facebook Profiles [-]")
#                     print(e)
#                     print("[-]")
#             else:
#                 print("Please provide Facebook Login Credentials in the social_mapper.py file") 
#         elif 'no_li' in person.tipo_socials:
#             if not (linkedin_username == "" or linkedin_password == ""):
                
#                 rc_peoplelist = fill_linkedin(rc_peoplelist)
                
#                 person.linkedin = rc_peoplelist[0].linkedin
#                 person.linkedinimage = rc_peoplelist[0].linkedinimage
#                 person.info_linkedin = rc_peoplelist[0].info_linkedin
#                 person.numero_social = rc_peoplelist[0].numero_social
#                 person.tipo_socials = rc_peoplelist[0].tipo_socials
#             else:
#                 print("Please provide LinkedIn Login Credentials in the social_mapper.py file")


# Pass peoplelist to modules for filling out
if args.a == True or args.fb == True:
    if not (facebook_username == "" or facebook_password == ""):
        try:
            peoplelist = fill_facebook(peoplelist)
        except Exception as e:
            print("[-] Error Filling out Facebook Profiles [-]")
            print(e)
            traceback.print_exc()
            print("[-]")
    else:
        print("Please provide Facebook Login Credentials in the social_mapper.py file")
if args.a == True or args.tw == True:
    if not (twitter_username == "" or twitter_password == ""):
        peoplelist = fill_twitter(peoplelist)
    else:
        print("Please provide Twitter Login Credentials in the social_mapper.py file")
if args.a == True or args.pin == True:
    if not (pinterest_username == "" or pinterest_password == ""):
        peoplelist = fill_pinterest(peoplelist)
    else:
        print("Please provide Pinterest Login Credentials in the social_mapper.py file")
if args.a == True or args.ig == True:
    if not (instagram_username == "" or instagram_password == ""):
        peoplelist = fill_instagram(peoplelist)
    else:
        print("Please provide Instagram Login Credentials in the social_mapper.py file")
if not args.format == "linkedint" and not args.format == "company":
    if args.a == True or args.li == True:
        if not (linkedin_username == "" or linkedin_password == ""):
            peoplelist = fill_linkedin(peoplelist)
        else:
            print("Please provide LinkedIn Login Credentials in the social_mapper.py file")
if args.a == True or args.vk == True:
    if not (vk_username == "" or vk_password == ""):
        peoplelist = fill_vkontakte(peoplelist)
    else:
        print("Please provide VK (VKontakte) Login Credentials in the social_mapper.py file")
if args.a == True or args.wb == True:
    if not (weibo_username == "" or weibo_password == ""):
        peoplelist = fill_weibo(peoplelist)
    else:
        print("Please provide Weibo Login Credentials in the social_mapper.py file")
if args.a == True or args.db == True:
    if not (douban_username == "" or douban_password == ""):
        peoplelist = fill_douban(peoplelist)
    else:
        print("Please provide Douban Login Credentials in the social_mapper.py file")
#re_check(peoplelist)

# Write out updated people list to a CSV file along with other output if
csv = []

if not os.path.exists("SM-Results"):
    os.makedirs("SM-Results")

if args.format == "csv":
    outputfilename = "SM-Results/results-Csv-social-mapper.csv"
    phishingoutputfilename = "SM-Results/results-Csv"
elif args.format == "imagefolder":
    outputfilename = "SM-Results/results-ImageFolder-social-mapper.csv"
    phishingoutputfilename = "SM-Results/results-ImageFolder"
else:
    outputfilename = "SM-Results/results-Company-social-mapper.csv"
    phishingoutputfilename = "SM-Results/results-Company"

filewriter = open(outputfilename.format(outputfilename), 'w')
titlestring = "Full Name,"
if args.a == True or args.li == True or args.format == "socialmapper":
    titlestring = titlestring + "LinkedIn,Cellulare,Sito Web,Email,Compleanno,Città,Impiego,Indirizzo,Messaggistica,Biografia,Formazione,Esperienze,"
    if args.email is not None:
        phishingoutputfilenamelinkedin = phishingoutputfilename + "-linkedin.csv"
        filewriterlinkedin = open(phishingoutputfilenamelinkedin.format(phishingoutputfilenamelinkedin), 'w')
if args.a == True or args.fb == True or args.format == "socialmapper":
    titlestring = titlestring + "Facebook,Work_and_Education,Placed_Lives,Contact_and_Basic_Info,Family_Relationships,Detail_about,"
    if args.email is not None:
        phishingoutputfilenamefacebook = phishingoutputfilename + "-facebook.csv"
        filewriterfacebook = open(phishingoutputfilenamefacebook.format(phishingoutputfilenamefacebook), 'w')
if args.a == True or args.tw == True or args.format == "socialmapper":
    titlestring = titlestring + "Twitter,Sito_Twitter,Città_Twitter,Twitter_Biografia,"
    if args.email is not None:
        phishingoutputfilenametwitter = phishingoutputfilename + "-twitter.csv"
        filewritertwitter = open(phishingoutputfilenametwitter.format(phishingoutputfilenametwitter), 'w')
if args.a == True or args.pin == True or args.format == "socialmapper":
    titlestring = titlestring + "Pinterest,"
    if args.email is not None:
        phishingoutputfilenamepinterest = phishingoutputfilename + "-pinterest.csv"
        filewriterpinterest = open(phishingoutputfilenamepinterest.format(phishingoutputfilenamepinterest), 'w')
if args.a == True or args.ig == True or args.format == "socialmapper":
    titlestring = titlestring + "Instagram,Biografi_Instagram,Sito_Personale_Instagram,"
    if args.email is not None:
        phishingoutputfilenameinstagram = phishingoutputfilename + "-instagram.csv"
        filewriterinstagram = open(phishingoutputfilenameinstagram.format(phishingoutputfilenameinstagram), 'w')
        
if args.a == True or args.vk == True or args.format == "socialmapper":
    titlestring = titlestring + "VKontakte,Data di Nascita,Città,Studiato a,Luogo di Nascita,Lingue,Cellulare,Telefono,Skype,College o università,Stato,Scuola,Gruppi,Azienda,Interesse,"
    if args.email is not None:
        phishingoutputfilenamevkontakte = phishingoutputfilename + "-vkontakte.csv"
        filewritervkontakte = open(phishingoutputfilenamevkontakte.format(phishingoutputfilenamevkontakte), 'w')
if args.a == True or args.wb == True or args.format == "socialmapper":
    titlestring = titlestring + "Weibo,"
    if args.email is not None:
        phishingoutputfilenameweibo = phishingoutputfilename + "-weibo.csv"
        filewriterweibo = open(phishingoutputfilenameweibo.format(phishingoutputfilenameweibo), 'w')
if args.a == True or args.db == True or args.format == "socialmapper":
    titlestring = titlestring + "Douban,"
    if args.email is not None:
        phishingoutputfilenamedouban = phishingoutputfilename + "-douban.csv"
        filewriterdouban = open(phishingoutputfilenamedouban.format(phishingoutputfilenamedouban), 'w')
titlestring = titlestring[:-1]

filewriter.write(titlestring)
filewriter.write("\n")

# Costruzione della file .csv estrapolando le informazioni dalle persone trovate
# Costruzione della file .csv per ogni persone, estrapolando le informazioni dalle foto di instangram di ogni persona
# Costruisco, per ogni social, prima la lista di label per le colonne del file e poi inserisco le informazioni
for person in peoplelist:
    if person.numero_social > 0:
        writestring = '"%s",' % (person.full_name)
        if args.email is not None:
            try:
                # Try to create email by replacing initials and names with persons name
                email = args.email.replace("<first>", person.first_name).replace("<last>", person.last_name).replace(
                    "<f>", person.first_name[0]).replace("<l>", person.last_name[0])
            except:
                email = "Error"
        # Controllo se richiesta ricerca su Linkein
        if args.a == True or args.li == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.linkedin) + '"%s",' % (person.info_linkedin["Cellulare"]) + '"%s",' % (person.info_linkedin["Sito Web"]) + '"%s",' % (
                              person.info_linkedin["Email"]) + '"%s",' % (
                              person.info_linkedin["Compleanno"]) + '"%s",' % (
                              person.info_linkedin["Città"]) + '"%s",' % (person.info_linkedin["Impiego"]) + '"%s",' % (person.info_linkedin["Indirizzo"])+ '"%s",' % (person.info_linkedin["Messaggistica"])+ '"%s",' % (
                                person.info_linkedin["Biografia"]) + '"%s",' % (person.info_linkedin["Formazione"]) + '"%s",' % (person.info_linkedin["Esperienze"])
            if person.linkedin != "" and args.email is not None:
                if email != "Error":
                    linkedinwritestring = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.linkedin,
                        person.linkedinimage,
                        person.info_linkedin["Cellulare"], person.info_linkedin["Sito Web"],
                        person.info_linkedin["Email"],
                        person.info_linkedin["Compleanno"], person.info_linkedin["Città"],
                        person.info_linkedin["Impiego"],person.info_linkedin["Indirizzo"],person.info_linkedin["Messaggistica"],
                        person.info_linkedin["Biografia"],person.info_linkedin["Formazione"],person.info_linkedin["Esperienze"])
                    filewriterlinkedin.write(linkedinwritestring)
        # Controllo se richiesta ricerca su Facebook
        if args.a == True or args.fb == True or args.format == "socialmapper":
           
            writestring = writestring + '"%s","%s","%s","%s","%s","%s",' % (
                person.facebook, person.info_facebook["Work_and_Education"], person.info_facebook["Placed_Lives"],
                person.info_facebook["Contact_and_Basic_Info"],person.info_facebook["Family_Relationships"],
                person.info_facebook["Detail_about"])

            if person.facebook != "" and args.email is not None:
                if email != "Error":
                    facebookwritestring = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.facebook,
                        person.facebookcdnimage,
                        person.info_facebook["Work_and_Education"], person.info_facebook["Placed_Lives"],
                        person.info_facebook["Contact_and_Basic_Info"],person.info_facebook["Family_Relationships"],
                        person.info_facebook["Detail_about"])
                    filewriterfacebook.write(facebookwritestring)
        # Controllo se richiesta ricerca su Twitter
        if args.a == True or args.tw == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.twitter) + '"%s",' % (
                person.info_twitter["Sito_twitter"]) + '"%s",' % (person.info_twitter["Città_twitter"]) + '"%s",' % (
                              person.info_twitter["Twitter_Biografia"])
            if person.twitter != "" and args.email is not None:
                if email != "Error":
                    twitterwritestring = '"%s","%s","%s","%s","%s","%s","%s","%s","%s",\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.twitter,
                        person.twitterimage,
                        person.info_twitter["Sito_twitter"], person.info_twitter["Città_twitter"],
                        person.info_twitter["Twitter_Biografia"])
                    filewritertwitter.write(twitterwritestring)

        # Controllo se richiesta ricerca su Pinterest
        if args.a == True or args.pin == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.pinterest)
            if person.pinterest != "" and args.email is not None:
                if email != "Error":
                    pinterestwritestring = '"%s","%s","%s","%s","%s","%s",\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.pinterest,
                        person.pinterestimage)
                    filewriterpinterest.write(pinterestwritestring)

        # Controllo se richiesta ricerca su Instagram
        if args.a == True or args.ig == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.instagram) + '"%s",' % (person.info_instagram["Biografia"])+ '"%s",' % (person.info_instagram["Sito_Personale"])
            if person.instagram != "" and args.email is not None:
                if email != "Error":
                    instagramwritestring = '"%s","%s","%s","%s","%s","%s","%s","%s"\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.instagram,
                        person.instagramimage, person.info_instagram['Biografia'],person.info_instagram['Sito_Personale'])
                    filewriterinstagram.write(instagramwritestring)
                
                

        # Controllo se richiesta ricerca su Vkontakte
        if args.a == True or args.vk == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.vk) + '"%s",' % str(
                person.info_vkontakte["Data di Nascita"]) + '"%s",' % str(
                person.info_vkontakte["Città"]) + '"%s",' % str(person.info_vkontakte["Studiato a"]) + '"%s",' % str(
                person.info_vkontakte["Luogo di Nascita"]) + '"%s",' % str(
                person.info_vkontakte["Lingue"]) + '"%s",' % str(
                person.info_vkontakte["Cellulare"]) + '"%s",' % str(person.info_vkontakte["Telefono"]) + '"%s",' % str(
                person.info_vkontakte["Skype"]) + '"%s",' % str(
                person.info_vkontakte["College o università"]) + '"%s",' % str(
                person.info_vkontakte["Stato"]) + '"%s",' % str(person.info_vkontakte["Scuola"]) + '"%s",' % str(
                person.info_vkontakte["Gruppi"]) + '"%s",' % str(person.info_vkontakte["Azienda"]) + '"%s",' % str(
                person.info_vkontakte["Interesse"])

            if person.vk != "" and args.email is not None:
                if email != "Error":
                    vkwritestring = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.vk, person.vkimage,
                        person.info_vkontakte["Data di Nascita"], person.info_vkontakte["Città"],
                        person.info_vkontakte["Studiato a"], person.info_vkontakte["Luogo di Nascita"],
                        person.info_vkontakte["Lingue"], person.info_vkontakte["Cellulare"],
                        person.info_vkontakte["Telefono"], person.info_vkontakte["Skype"],
                        person.info_vkontakte["College o università"], person.info_tinfo_vkontaktewitter["Stato"],
                        person.info_vkontakte["Scuola"], person.info_vkontakte["Gruppi"],
                        person.info_vkontakte["Azienda"], person.info_vkontakte["Interesse"])
                    filewritervkontakte.write(vkwritestring)

        # Controllo se richiesta ricerca su Weibo
        if args.a == True or args.wb == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.weibo)
            if person.weibo != "" and args.email is not None:
                if email != "Error":
                    weibowritestring = '"%s","%s","%s","%s","%s","%s"\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.weibo, person.weiboimage)
                    filewriterweibo.write(weibowritestring)

        # Controllo se richiesta ricerca su Douban
        if args.a == True or args.db == True or args.format == "socialmapper":
            writestring = writestring + '"%s",' % (person.douban)
            if person.douban != "" and args.email is not None:
                if email != "Error":
                    doubanwritestring = '"%s","%s","%s","%s","%s","%s"\n' % (
                        person.first_name, person.last_name, person.full_name, email, person.douban, person.doubanimage)
                    filewriterdouban.write(doubanwritestring)

        writestring = writestring[:-1]
        
        filewriter.write(((writestring).encode('ascii', 'ignore').decode('ascii'))+'')
        filewriter.write("\n")

        terminalstring = ""
        # print "\n" + person.full_name
        if person.linkedin != "":
            terminalstring = terminalstring + "\tLinkedIn: " + person.linkedin + "\n"
        if person.facebook != "":
            terminalstring = terminalstring + "\tFacebook: " + person.facebook + "\n"
        if person.twitter != "":
            terminalstring = terminalstring + "\tTwitter: " + person.twitter + "\n"
        if person.pinterest != "":
            terminalstring = terminalstring + "\tPinterest: " + person.pinterest + "\n"
        if person.instagram != "":
            terminalstring = terminalstring + "\tInstagram: " + person.instagram + "\n"
        if person.vk != "":
            terminalstring = terminalstring + "\tVkontakte: " + person.vk + "\n"
        if person.weibo != "":
            terminalstring = terminalstring + "\tWeibo: " + person.weibo + "\n"
        if person.douban != "":
            terminalstring = terminalstring + "\tDouban: " + person.douban + "\n"

print("\nResults file: " + outputfilename)
filewriter.close()



# Close all the filewriters that may exist
try:
    if filewriterlinkedin:
        filewriterlinkedin.close()
except:
    pass
try:
    if filewriterfacebook:
        filewriterfacebook.close()
except:
    pass

try:
    if filewritertwitter:
        filewritertwitter.close()
except:
    pass
try:
    if filewriterpinterest:
        filewriterpinterest.close()
except:
    pass
try:
    if filewriterinstagram:
        filewriterinstagram.close()
except:
    pass
try:
    if filewritervkontakte:
        filewritervkontakte.close()
except:
    pass
try:
    if filewriterweibo:
        filewriterweibo.close()
except:
    pass
try:
    if filewriterdouban:
        filewriterdouban.close()
except:
    pass

# Code for generating HTML file
if args.format == "csv":
    htmloutputfilename = "SM-Results/results-Csv-social-mapper.html"
elif args.format == "imagefolder":
    htmloutputfilename = "SM-Results/results-ImageFolder-social-mapper.html"
else:
    htmloutputfilename = "SM-Results/results-Company-social-mapper.html"
# filewriter = open(htmloutputfilename.format(htmloutputfilename), 'w')
# # background-color: #4CAF50;
# css = """<meta charset="utf-8" />
# <style>
#     #employees {
#         font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
#         border-collapse: collapse;
#         width: 100%;
#     }

#     #employees td, #employees th {
#         border: 1px solid #ddd;
#         padding: 8px;
#     }

#     #employees td {
#         height: 100px;
#     }

#     #employees tbody:nth-child(even){
#         background-color: #f2f2f2;
#     }

#     #employees th {
#         padding-top: 12px;
#         padding-bottom: 12px;
#         text-align: left;
#         background-color: #12db00;
#         color: white;
#     }


#     #employees .hasTooltipleft span {
#         visibility: hidden;
#         background-color: black;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px 0;

#         /* Position the tooltip */
#         position: absolute;
#         left:15%;
#         z-index: 1;

#     }

#     #employees .hasTooltipcenterleft span {
#         visibility: hidden;
#         background-color: black;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px 0;

#         /* Position the tooltip */
#         position: absolute;
#         left:20%;
#         z-index: 1;

#     }

#     #employees .hasTooltipcenterright span {
#         visibility: hidden;
#         background-color: black;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px 0;

#         /* Position the tooltip */
#         position: absolute;
#         left:25%;
#         z-index: 1;

#     }

#     #employees .hasTooltipright span {
#         visibility: hidden;
#         background-color: black;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px 0;

#         /* Position the tooltip */
#         position: absolute;
#         left:30%;
#         z-index: 1;

#     }

#     #employees .hasTooltipfarright span {
#         visibility: hidden;
#         background-color: black;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px 0;

#         /* Position the tooltip */
#         position: absolute;
#         left:35%;
#         z-index: 1;

#     }

#     #employees .hasTooltipleft:hover span {
#         visibility: visible;
#     }

#     #employees .hasTooltipcenterleft:hover span {
#         visibility: visible;
#     }

#     #employees .hasTooltipcenterright:hover span {
#         visibility: visible;
#     }

#     #employees .hasTooltipright:hover span {
#         visibility: visible;
#     }

#     #employees .hasTooltipfarright:hover span {
#         visibility: visible;
#     }

#     #employees tbody:hover {
#         background-color: #aaa;
#     }
# }

# </style>
# """
# foot = "</table></center>"
# header = """<center><table id=\"employees\">
#             <tr>
#                 <th rowspan=\"2\">Photo</th>
#                 <th rowspan=\"2\">Name</th>
#                 <th>LinkedIn</th>
#                 <th>Facebook</th>
#                 <th>Twitter</th>
#                 <th>Pinterest</th>
#                 <th>Instagram</th>
#             </tr>
#             <tr>
#                 <th>-</th>
#                 <th>VKontakte</th>
#                 <th>Weibo</th>
#                 <th>Douban</th>
#             </tr>
#              """
# filewriter.write(css)
# filewriter.write(header)
# for person in peoplelist:

#     if person.person_imagelink.startswith("http"):
#         link_image = person.person_imagelink
#     else:
#         link_image = "./." + person.person_imagelink
#     body = "<tbody>" \
#            "<tr>" \
#            "<td class=\"hasTooltipleft\" rowspan=\"2\"><img src=\"%s\" width=auto height=auto style=\"max-width:200px; max-height:200px;\">" \
#            "<td rowspan=\"2\">%s</td>" \
#            "<td class=\"hasTooltipcenterleft\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>LinkedIn:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipcenterright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Facebook:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Twitter:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Pinterest:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipfarright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Instagram:<br>%s</span></a></td>" \
#            "</tr>" \
#            "<tr>" \
#            "<td class=\"hasTooltipcenterleft\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>-:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipcenterright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>VKontakte:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Weibo:<br>%s</span></a></td>" \
#            "<td class=\"hasTooltipfarright\"><a href=\"%s\"><img src=\"%s\" onerror=\"this.style.display=\'none\'\" width=auto height=auto style=\"max-width:100px; max-height:100px;\"><span>Douban:<br>%s</span></a></td>" \
#            "</tr>" \
#            "</tbody>" % (
#                link_image, person.full_name, person.linkedin, person.linkedinimage, person.linkedin, person.facebook,
#                person.facebookcdnimage, person.facebook, person.twitter, person.twitterimage, person.twitter,
#                person.pinterest, person.pinterestimage, person.pinterest, person.instagram, person.instagramimage,
#                person.instagram, "", "", "", person.vk, person.vkimage, person.vk, person.weibo, person.weiboimage,
#                person.weibo, person.douban, person.doubanimage, person.douban)
#     filewriter.write(body)

# filewriter.write(foot)
# print("HTML file: " + htmloutputfilename + "\n")
# filewriter.close()


# copy images from Social Mapper to output folder
# outputfoldername = "SM-Results/" + args.input.replace("\"", "").replace("/", "-") + "-social-mapper"
outputfoldername = ".\Potential_target_image"
if args.format != "imagefolder":
    # os.rename('temp-targets', outputfoldername)
    print("Image folder: " + outputfoldername + "\n")

# if os.path.exists('.\Potential_target_image'):
#    shutil.rmtree('.\Potential_target_image')


# print datetime.now() - startTime
# completiontime = datetime.now() - startTime

print("Task Duration: " + str(datetime.now() - startTime))
