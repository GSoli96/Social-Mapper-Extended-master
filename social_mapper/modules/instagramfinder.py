# -*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from time import sleep
import sys
import os
from bs4 import BeautifulSoup

import traceback

# Classe concreta che istanzia il crawler per il social Instagram
class Instagramfinder(object):
    timeout = 10 #timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler
    


    #
    # Metodo init per settare proprietà del browser
    #
    # @param showbrowser Stringa legata al comando da console, se presente si richiede la visine in real-time della ricerca
    #
    def __init__(self, showbrowser):
        #display = Display(visible=0, size=(1600, 1024))
        #display.start()
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
        self.driver.get("https://www.instagram.com/accounts/login/?hl=en")
        self.driver.execute_script('localStorage.clear();')
        
        # convert unicode in instagram title to spaces for comparison
        titleString = ''.join([i if ord(i) < 128 else ' ' for i in self.driver.title])
        
        if (titleString.startswith("Login")):
            
            print("\n[+] Instagram Login Page loaded successfully [+]")
            
            try:
                sleep(2)
               
                #Button Login
                self.driver.find_element_by_xpath('/html/body/div[4]/div/div/button[1]').click()
                
            except:
                print("Instagram Login Page Button Login field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                pass

            sleep(2)
            #try ricerca campo login, se trovato invia username
            try:
                
                instagramUsername = self.driver.find_element_by_xpath('//input[@name="username"]')
                
                instagramUsername.send_keys(username)
                
            except:
                print("Instagram Login Page password field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                pass
            #try ricerca campo password, se trovato invia pasword
            sleep(2)
            try:
                
                instagramPassword = self.driver.find_element_by_xpath('//input[@name="password"]')
               
                instagramPassword.send_keys(password)
                
            except:
                print("Instagram Login Page password field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                pass
            #try ricerca button login, se trovato clicca e effettua login
            sleep(2)
           
            try:
               
                #Button Login 
                self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button/div').click()
               
            except:
                print("Instagram Login Page Button Login field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                pass
            
            sleep(2)
            try:
                
            #bypassare save info instagram
                self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button').click()  
               
            except:
                
                pass
           
            sleep(3)
            
            if (self.driver.title.encode('utf8', 'replace') == (bytes("Instagram", 'utf-8'))):
                
                print("[+] Instagram Login Success [+]\n")
                
                #Button not now, save your login info(not now)
                try:
                 
                    self.driver.find_element_by_xpath('//button[@type="button"]').click()
    
                  


                except:
                    print("Closing Message Failed or did not exist")
                    pass
             
            else:
               
                print("[-] Instagram Login Failed [-]\n")
        
        else:
           
            print(
                "Instagram Login Page title field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")

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
    def getInstagramProfiles(self, first_name, last_name, username, password):
        sleep(2)
        picturelist = []
        try:
            url = "https://www.instagram.com/?hl=en"
            self.driver.get(url)
            sleep(2)
            
            
            try:
                searchbar = self.driver.find_element_by_xpath("//input[@placeholder='Search']")
            except:
                # if cant find search bar try to relogin
                self.doLogin(username, password)
                self.driver.get(url)
                sleep(2)
                try:
                    searchbar = self.driver.find_element_by_xpath("//input[@placeholder='Search']")
                except:
                    print("Instagram Timeout Error, session has expired and attempts to reestablish have failed")
                    return picturelist
           
            # effettua la ricerca compilando il campo con il nome della persone richiesta
            full_name = first_name + " " + last_name
            searchbar.send_keys(full_name)
            sleep(3)
            searchresponse = self.driver.page_source.encode('utf-8')
            soupParser = BeautifulSoup(searchresponse, 'html.parser')
            try:
                list_people= soupParser.findAll('div', {'class': '_abm4'})
                
                # per ogni persona risultante dalla ricerca, ne estrapola la foto
                
                for element in list_people:

                    
                    link_tmp = element.find('a')['href']
                    if(link_tmp!="/"):
                        link = link_tmp
                    
                    profilepic = element.find('img', {'class': '_aa8j'})['src']
                    try:
                        if element.find('span', {'class', '_9_1f _aa5a'})['aria-label'] == 'Verified':                               
                            picturelist.append(["https://instagram.com" + link, profilepic, True])
                            break
                        

                    except Exception as a:
                        #traceback.print_exc()
                        #print(a)
                        picturelist.append(["https://instagram.com" + link, profilepic, False])
                        continue
                
            except Exception as e:
                #traceback.print_exc()
                #print(e)
                pass

        except Exception as e:
            #print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno) + "\n"+e)
            picturelist = []
            # print "Error"
            pass
        return picturelist

    #
    # Metodo che estrae tutti i link e l'attributo alt di ogni immagine di una persona su instagram
    #
    # @param post_ig Lista di Stringhe che contiene il link e l'attributo alt di ogni immagine
    # @param number_post Intero che rappresenta il numero di post pubblicati da una persona
    # @param name Stringa che rappresenta il nome della persona
    #
    # @return post_ig Lista delle immagini e alt che sono state estrapolate dal profilo
    #
    def get_links(self,post_ig,number_post,name):
            
            #cerco le immagini dei post sul profilo instagram
            list_img= self.driver.find_elements_by_xpath("//img[@class='x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3']")
            # per ogni immagine risultante dalla ricerca, ne estrapola il link e l'alt
            for image in list_img:
                try:

                    link = image.get_attribute("src")
                    alt_img = image.get_attribute("alt")
                    alt = ((alt_img.encode('ascii', 'ignore')).decode('ascii'))
                    tupla = (link, (alt.replace("\n", " ").strip()))
                    if tupla not in post_ig:
                        post_ig.append(tupla)
                    elif tupla in post_ig:
                        continue
                    
                    sys.stdout.write(
                        "\rInstagram Post Found: %i/%i  : %s                            " % (len(post_ig), number_post, name))
                    sys.stdout.flush()
                except Exception as e:
                    #traceback.print_exc()
                    #print(e)
                    continue 
            return post_ig     

    #
    # Metodo che permete lo scroll della pagina del profilo instagram
    #
    # @param speed Intero che rappresenta di quanto la pagina dovrà scrollare
    # @param number_post Intero che rappresenta il numero di post pubblicati da una persona
    # @param name Stringa che rappresenta il nome della persona
    #
    # @return post Lista di tuple, dove ognuna contiene i post che sono state estrapolati dal profilo
    #
    def scroll_down_page(self, speed,number_post, name):
        post=[]
        current_scroll_position, new_height= 0, 1
        while current_scroll_position <= new_height:
            sleep(1)
            post=  self.get_links(post,number_post, name)
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
        return post
        

    #
    # Metodo che estrae tutti i post di una persona su instagram
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param person variabile di tipo Person che rappresenta la persona trovata su instangram
    #
    def extract_Instagramimage(self,username, password, person):
        
        sleep(1)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(username, password)
            print('login non valido')
            sleep(3)
            if "login" in self.driver.current_url:
                print("Instagram Timeout Error, session has expired and attempts to reestablish have failed")
        
        
        self.driver.get(person.instagram)
        self.driver.maximize_window()
        sleep(2)
        
        number_post_text = self.driver.find_element_by_xpath("//*[@class='_ac2a']").text
        number_post=0
        try:            
            number_post = int(number_post_text.replace(" ","").replace(".", "").replace(",",""))
        except Exception as e:
            # traceback.print_exc(); print(e)
            pass
        post=[]
        try:
            outputDir_InfoIG = "SM-Results\\raccolta_info_imageIG\\"+person.full_name
            
            if not os.path.exists(outputDir_InfoIG):
                os.makedirs(outputDir_InfoIG)

            outputfilename_InfoIG = outputDir_InfoIG+"\\Info_img_Instagram_"+person.full_name+".csv"
            filewriter_InfoIG = open(outputfilename_InfoIG.format(outputfilename_InfoIG), 'w')
            titlestring_InfoIG = "link_Img,alt_Img" 
            filewriter_InfoIG.write(titlestring_InfoIG)
            filewriter_InfoIG.write("\n")

            if(number_post>0):
                post= self.scroll_down_page(250, number_post,person.full_name)
                for tupla in post:
                    try:
                        tmp = str(tupla[0]) + " , "+ str(tupla[1])+"\n"
                        filewriter_InfoIG.write(tmp)   
                    except Exception as e:
                        #traceback.print_exc(); print(e)
                        continue
                filewriter_InfoIG.close()
            elif (number_post==0):
                #print("No posts found")
                filewriter_InfoIG.close()
                os.remove(outputfilename_InfoIG)
        except Exception as e:
            # traceback.print_exc(); print(e)
            pass



    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return instagram Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataInstagram(self, username, password, url):
        
        instagram = {"Biografia": "", "Sito_Personale": ""}
        self.driver.get(url)
        sleep(1)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(username, password)
            print('login non valido')
            sleep(3)
            if "login" in self.driver.current_url:
                print("Instagram Timeout Error, session has expired and attempts to reestablish have failed")
        

        # estrapolo la Biografia della persona trovata
        biografia = ""
        
        try:
            container = self.driver.find_elements_by_xpath('//div[@class="_aacl _aacp _aacu _aacx _aad6 _aade"]')
            biografia= ((container[3].text).encode('ascii', 'ignore').decode('ascii'))+''
            instagram['Biografia'] = biografia.replace('\n', ' ')

        except Exception as e: 
            # traceback.print_exc(); print(e)
            instagram['Biografia']=""
            pass
        
        
    #ESTRAPOLA DATI dal sito personale, se presente  
        try:

            tmp_driver_site = self.driver.find_element_by_class_name('_aa_c')
            tmp_driver_site_tag= tmp_driver_site.find_element_by_tag_name('a')
            tmp_sito= tmp_driver_site_tag.get_attribute('href')
            instagram['Sito_Personale']=tmp_sito
        except Exception as e:
            # traceback.print_exc(); print(e)
            instagram['Sito_Personale']=""
            pass
    
        
        return instagram

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
    