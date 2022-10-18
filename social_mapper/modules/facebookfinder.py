# -*- coding: utf-8 -*-
from __future__ import print_function
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import os
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

# Classe concreta che istanzia il crawler per il social Facebook
class Facebookfinder(object):
    timeout = 5 #timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler
    #
    # Metodo init per settare proprietà del browser
    #
    # @param showbrowser Stringa legata al comando da console, se presente si richiede la visine in real-time della ricerca
    #
    def __init__(self, showbrowser):
        # display = Display(visible=0, size=(1600, 1024))
        # display.start()
        if not showbrowser:
            os.environ['MOZ_HEADLESS'] = '1'
        firefoxprofile = webdriver.FirefoxProfile()
        firefoxprofile.set_preference("permissions.default.desktop-notification", 1)
        firefoxprofile.set_preference("dom.webnotifications.enabled", 1)
        firefoxprofile.set_preference("dom.push.enabled", 1)
        self.driver = webdriver.Firefox(firefox_profile=firefoxprofile)
        self.driver.implicitly_wait(3)
        self.driver.delete_all_cookies()

    #
    # Metodo che effettua il login al social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    def doLogin(self, username, password):
        self.driver.get("https://www.facebook.com/login")
        self.driver.execute_script('localStorage.clear();')
        #Bypassare Banner dei Cookie di Facebook
        self.driver.implicitly_wait(10)
        try:

            self.driver.find_element_by_xpath('//*[@class="_42ft _4jy0 _9xo6 _4jy3 _4jy1 selected _51sy"]').click()
        except:
            pass
        sleep(2)

        if (self.driver.title.encode('ascii', 'replace').endswith(bytes("Facebook", 'utf-8'))):
            print("\n[+] Facebook Login Page loaded successfully [+]")
            try:
                #textfield email
                fbUsername = self.driver.find_element_by_id("email")
                fbUsername.send_keys(username)
                sleep(2)
                #textfield password
                fbPassword = self.driver.find_element_by_id("pass")
                fbPassword.send_keys(password)
                sleep(2)
                #loginbutton
                ActionChains(self.driver).move_to_element(self.driver.find_element_by_id("loginbutton")).click().perform()
           
                sleep(5)
                self.driver.get("https://www.facebook.com")
            except:
                pass
            
            try:
                sleep(2)
                if (str(self.driver.title.encode('utf8', 'replace')) == str(bytes("Facebook", 'utf-8'))):
                            print("[+] Facebook Login Success [+]\n")
                else:
                            print("[-] Facebook Login Failed [-]\n")
            except:
                pass
            

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param first_name Stringa che rappresenta il nome della persona da cercare
    # @param last_name Stringa che rappresenta il cognome della persona da cercare
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    # @return picturelist Array di persone trovare rispetto al nome in input
    #
    def getFacebookProfiles(self, first_name, last_name, username, password):
        # effettuo la ricerca, compilando il campo apposito
        url = "https://www.facebook.com/search/people/?q=" + first_name + "%20" + last_name
        self.driver.get(url)
        sleep(3)
        picturelist = []

        # verifica se il sessione è ancora valida, in caso negativo la ricrea rieseguendo i login e rieffettua la ricerca
        if (self.driver.title.encode('utf8', 'replace').split()[1].startswith(
                bytes(first_name, 'utf-8')) == False and self.driver.title.encode('utf8', 'replace').startswith(
            bytes(first_name, 'utf-8')) == False):
            print("\nFacebook session has expired, attempting to reestablish...")
            self.doLogin(username, password)
            self.driver.get(url)
            sleep(3)
            if (self.driver.title.encode('utf8', 'replace').split()[1].startswith(
                    bytes(first_name, 'utf-8')) == False and self.driver.title.encode('utf8', 'replace').startswith(
                bytes(first_name, 'utf-8')) == False):
                print("Facebook Timeout Error, session has expired and attempts to reestablish have failed")
                return picturelist
            else:
                print("New Facebook Session created, resuming mapping process")
       
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        # per ogni persona risultante dalla ricerca, ne estrapola la foto
        count=0
        list_person= soupParser.findAll('a', {'class': 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f'})
        fullname = first_name + " " + last_name
        for element in list_person:
            try:
                
                if((first_name +" "+ last_name)==(element.text)):
                    
                #Recupero link al profilo
                    link = element['href'] 
                    self.driver.get(link)
                    searchresponse1 = self.driver.page_source.encode('utf-8')
                    soupParser1 = BeautifulSoup(searchresponse1, 'html.parser')
                    sleep(2)

                #Recupero il link all'immagine grande                    
                    try:
                        element1 = soupParser1.find('svg', {'class':'x3ajldb','role':"img",'aria-label':fullname})
                        link_img = element1.find('image')['xlink:href']

                    except Exception as e:
                        continue
                    
                    self.driver.get(link_img)
                    searchresponse2 = self.driver.page_source.encode('utf-8')
                    soupParser2 = BeautifulSoup(searchresponse2, 'html.parser')
                    cdnpicture=""
                    sleep(2)    

                #Recupero immagine grande
                    try:
                        cdnpicture = soupParser2.find('img')['src']
                    except Exception as e:                            
                            continue
                              
            except Exception as e:
                continue

            profilepic=""
            picturelist.append([link, profilepic, 1.0, cdnpicture])
            if(count>=5):
                break
            count=count+1
        return picturelist

    #
    # Metodo che estrepola le informazioni circa la persona trovata
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return facebook Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataFacebook(self, username, password, url):
        tag_html = "span" 
        info = ""
        facebook = {"Work_and_Education": "", "Placed_Lives": "", "Contact_and_Basic_Info": "","Family_Relationships": "", "Detail_about": ""}
        
        if "profile.php" in url:
            url = url.split("&")[0]
        elif "profile.php" not in url:
            url = url.split("?")[0]

        self.driver.get(url)

        # verifico se il login è ancora valido, altrimenti lo rieseguo (max 2 volte)
        if "login" in self.driver.current_url:
            self.doLogin(username, password)

            if "login" in self.driver.current_url:
                print("Facebook Timeout Error, session has expired and attempts to reestablish have failed")
        searchresponse = self.driver.page_source.encode('utf-8')
        sleep(2)

        
        # carico la sezione Work_and_Education
        self.driver.get(url + "/about_work_and_education")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)

        # estrapolo le informazioni nella sezione Work_and_Education della persona trovata
        for element in soupParser.find_all(tag_html, {'class': 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'}):
            try:
                if ( element.text != "Facebook"):
                    info = info + element.text + "\\"
            except Exception as e:
                continue

        if "No workplaces to show\\No schools to show\\" == info or "Add a workplace\\Add a professional skill\\Add a college\\Add a high school\\" == info:
            facebook["Work_and_Education"] = ""
        else:
            app = str(info[:-1])
            facebook["Work_and_Education"] = app

        # carico la sezione Placed_Lives
        info = ""
        
        self.driver.get(url + "/about_places")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)

        # estrapolo le informazioni nella sezione Placed_Lives della persona trovata
        try:
            currentCity= self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/span/a/span/span")
            info = info + currentCity.text + "(Current city)\\"

            hometown= self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]/span/a/span/span")
            info = info + hometown.text + "(Hometown)\\"
        except Exception as e:
            pass

        if "Add your current city\\Add your hometown\\Add a place\\" == info or "No current city to show\\No hometown to show\\No place to show\\" == info:
            facebook["Placed_Lives"] = ""
        else:
            app = str(info[:-1])
            facebook["Placed_Lives"] = app

        # carico la sezione Contact e Basic_Info
        info = ""
        
        self.driver.get(url + "/about_contact_and_basic_info")
       
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)

        # estrapolo le informazioni nelle sezioni Contact e Basic_Info della persona trovata
        for element in soupParser.findAll(tag_html, {'class': 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'}):
            try:
                if(element.text != "UnreadYou're not in any groups yet. Join groups to find other people who share your interests."):
                    info = info + element.text + "\\"
            except Exception as e:
                #print(e)
               continue
        if "No contact info to show\\No links to show\\" == info or "No links to show\\" == info or "No contact info to show\\" == info or "No contact info to show\\No links to show" == info:
            facebook["Contact_and_Basic_Info"] = ""
        else:
            app = str(info[:-1])
            facebook["Contact_and_Basic_Info"] = app


        # Families and Relationship
        info = ""
        relationship=""
        fmembers1=""
        fmembers2=""
        self.driver.get(url + "/about_family_and_relationships")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)
        
        # estrapolo le informazioni nelle sezioni Families and Relationship della persona trovata
        try:
            relationship = self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[1]/span/a/span/span")
            info = info + relationship.text + "(Relationship)\\"
        except Exception as e:
            pass

        try:
            fmembers1= self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div/div[2]/div[1]/span/a/span/span")
        except Exception as e:
            fmembers1=""
            pass

        try:
            fmembers2= self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div[2]/div[3]/div/div/div[2]/div[1]/span/a/span/span")
        except Exception as e:
            fmembers2=""
            pass
        try:
            if(fmembers1!="")and(fmembers2!=""):
                info = info + fmembers1.text + ", "+fmembers2.text +" (Family members)\\"
            if(fmembers1=="")and(fmembers2!=""):
                info = info +fmembers2.text +" (Family members)\\"
            if(fmembers1!="")and(fmembers2==""):
                info = info +fmembers1.text +" (Family members)\\"
            if(fmembers1=="")and(fmembers2==""):
                info = info + ""

            if "No relationship info to show\\No family members to show" == info:
                facebook["Family_Relationships"] = ""
            app = str(info[:-1])
            facebook["Family_Relationships"] = app

        except Exception as e:
            facebook["Family_Relationships"]=""
            pass
        

        # carico la sezione Detail_about
        info = ""
        self.driver.get(url + "/about_details")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)

        # estrapolo le informazioni nella sezione Detail_about della persona trovata
        for element in soupParser.findAll(tag_html, {'class': 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'}):
            try:
                info = info + element.text + "\\"
            except Exception as e:
                continue
        if "No additional details to show\\No favorite quotes to show\\No name pronunciation to show" in info:
            facebook["Detail_about"] = ""
        else:
            app = str(info[:-1])
            facebook["Detail_about"] = app

        return facebook

    #
    # Metodo che restituisce tutti i cookies presenti
    #
    def getCookies(self):
        all_cookies = self.driver.get_cookies()
        cookies = {}
        for s_cookie in all_cookies:
            cookies[s_cookie["name"]] = s_cookie["value"]
        return cookies

    #
    # Metodo che elimina tutti i cookies presenti
    #
    def testdeletecookies(self):
        self.driver.delete_all_cookies()

    #
    # Metodo che termnina la sessione
    #
    def kill(self):
        self.driver.quit()
