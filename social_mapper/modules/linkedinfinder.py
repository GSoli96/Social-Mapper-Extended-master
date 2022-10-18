# -*- coding: utf-8 -*-
from __future__ import print_function
from imp import source_from_cache
from operator import concat
import sys
import re
import traceback
import os
from itertools import repeat
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
import shutil

# Classe concreta che istanzia il crawler per il social Linkedin
class Linkedinfinder(object):
    timeout = 1 #timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler

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
        self.driver.get("https://www.linkedin.com/uas/login")
        self.driver.execute_script('localStorage.clear();')
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)

        if (self.driver.title.encode('ascii', 'replace').startswith(bytes("Accesso a LinkedIn, Accesso | LinkedIn", 'utf-8'))):
            print("\n[+] LinkedIn Login Page loaded successfully [+]")            
            try:
                #textfield username
                lnkUsername = self.driver.find_element_by_id("username")
                lnkUsername.send_keys(username)
            except:
                print("LinkedIn Login Page username field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            try:
                #textfield password
                lnkPassword = self.driver.find_element_by_id("password")
                lnkPassword.send_keys(password)
            except:
                print("LinkedIn Login Page username field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            sleep(2)
            try:
                #button login
                self.driver.find_element_by_xpath('/html/body/div/main/div[3]/div[1]/form/div[3]/button').click()
                
            except:
                print("LinkedIn Login Page username field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            sleep(2)

            if (self.driver.title.encode('utf8', 'replace') == bytes("Accesso a LinkedIn, Accesso | LinkedIn", 'utf-8')):
                print("[-] LinkedIn Login Failed [-]\n")
            else:
                print("[+] LinkedIn Login Success [+]\n")
        else:
            print(
                "LinkedIn Login Page title field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
        sleep(10)
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
    def getLinkedinProfiles(self, first_name, last_name, username, password):
        picturelist = []
        url = "https://www.linkedin.com/search/results/people/?keywords=" + first_name + "%20" + last_name + "&origin=SWITCH_SEARCH_VERTICAL"
        self.driver.get(url)
        sleep(3)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(username, password)
            self.driver.get(url)
            sleep(3)
            if "login" in self.driver.current_url:
                print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
                return picturelist
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')

        # LinkedIn has implemented some code to say no results seemly at random, need code to research if this result pops.
        ## Anti Scraping Bypass (Try 3 times before skipping):
        # If there are no results do check
        #if (len(soupParser.find_all('div', {'class': 'search-result__image-wrapper'})) == 0):
        if (len(soupParser.find_all('div', {'class': 'display-flex align-items-center'})) == 0):
            # If there is the no results page do an additional try
            if (len(soupParser.find_all('div', {'class': 'search-no-results__image-container'})) != 0):
                self.driver.get(url)
                if "login" in self.driver.current_url:
                    self.doLogin(username, password)
                    self.driver.get(url)
                    
                    if "login" in self.driver.current_url:
                        print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
                        return picturelist
                searchresponse = self.driver.page_source.encode('utf-8')
                soupParser = BeautifulSoup(searchresponse, 'html.parser')
                #conteiner dei risultati della ricerca
                if (len(soupParser.find_all('div', {'class': 'entity-result__item'})) == 0): #se non ci sono risultati check 1
                    #testo no result found
                    if (len(soupParser.find_all('h2', {'class': 'artdeco-empty-state__headline artdeco-empty-state__headline--mercado-empty-room-small '+
                                                                   'artdeco-empty-state__headline--mercado-spots-small'})) != 0): #se ci sono h1 con quella classe allora non ci sono risultati
                        
                        self.driver.get(url)
                        if "login" in self.driver.current_url:
                            self.doLogin(username, password)
                            self.driver.get(url)
                            if "login" in self.driver.current_url:
                                print(
                                    "LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
                                return picturelist
                        searchresponse = self.driver.page_source.encode('utf-8')
                        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(2)
        try:
            # per ogni persona risultante dalla ricerca, ne estrapola la foto
           
            el1 = soupParser.find_all('div', {'class': 'entity-result'})
            for element in el1:
                try:
                    link = element.find('a', {'aria-hidden': 'true', 'data-test-app-aware-link':''})['href']
                    profilepic = element.find('img')['src']
                    picturelist.append([link, profilepic, 1.0])
                except Exception as e:
                    #traceback.print_exc()
                    #print(e)
                    continue
          
        except Exception as e:
            #traceback.print_exc()
            #print(e)
            pass


        return picturelist

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return info Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataLinketin(self, username, password, url, full_name):
        
        info = {"Cellulare": "", "Sito Web": "", "Email": "", "Compleanno": "", "Città": "",
                "Impiego": "", "Indirizzo": "", "Messaggistica":"", "Biografia":"", "Formazione":"","Esperienze":""}

        self.driver.get(url)
        sleep(2)

        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(username, password)
            sleep(3)
            if "login" in self.driver.current_url:
                print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(1)

        # estrapolo le informazioni circa l'impiego
        try:
            element = self.driver.find_element_by_xpath('//*[@class="text-body-medium break-words"]')
            impiego = str(element.text)
            info["Impiego"] = ((impiego.encode('ascii', 'ignore')).decode('ascii')) 
            
        except Exception as e:
            #print(e)
            pass

        # estrapolo le informazioni circa la città di residenza
        try:
            element1 = self.driver.find_element_by_xpath('//*[@class="text-body-small inline t-black--light break-words"]')
            residenza = str(element1.text.strip())
            
            info["Città"] = ((residenza.encode('ascii', 'ignore')).decode('ascii')) 
            
        except Exception as e:
            #print(e)
            pass
        
        biografia=""
        esperienze=""
        formazione=""
        # estrapolo le informazioni circa la persona, esperienze e formazione
        try:
            element2 = self.driver.find_element_by_xpath('//*[@class="display-flex ph5 pv3"]')
            element_tmps = element2.find_elements_by_xpath('//*[@class="visually-hidden"]')
            about=False
            experience=False
            education=False
            for element_tmp in element_tmps:
                text_tmp = str(element_tmp.text)
                if((text_tmp!="Experience")and(text_tmp!="About")and(text_tmp!="Education")and(text_tmp!=" ")and(text_tmp!="")):
                    if(about):
                        biografia = biografia + " " + text_tmp
                    elif(experience):
                        esperienze = esperienze + " " + text_tmp
                    elif(education):
                        formazione = formazione + " " + text_tmp


                if(text_tmp=="About"):
                    about=True
                    experience=False
                    education=False
                    continue
                elif(text_tmp=="Experience"):
                    about=False
                    experience=True
                    education=False
                    continue
                elif(text_tmp=="Education"):
                    about=False
                    experience=False
                    education=True
                    continue
                
                if(text_tmp=="Interests")or(text_tmp=="Influencers")or(text_tmp=="Companies"):
                    break

            info["Biografia"] = ((biografia.encode('ascii', 'ignore')).decode('ascii'))  
            info["Esperienze"] = ((esperienze.encode('ascii', 'ignore')).decode('ascii'))  
            info["Formazione"] = ((formazione.encode('ascii', 'ignore')).decode('ascii'))  

        except Exception as e:
            #traceback.print_exc()
            #print(e)
            pass
        
        #estrapolo il curriculum
        try:
            list_button_more = self.driver.find_elements_by_xpath('//button[@aria-expanded="false" and @aria-label="More actions" and @type="button" and @tabindex="0"]') #menu button more        
            
            #WebDriver
            after_button_more = self.driver.find_element_by_xpath('//div[@class="artdeco-dropdown__content-inner"]') #conteiner menu button more        
            class_after_button_more= after_button_more.get_attribute("class")   #conteiner menu button more  

            #Beautiful Soap 
            searchresponse1 = self.driver.page_source.encode('utf-8')
            soupParser1 = BeautifulSoup(searchresponse1, 'html.parser')
            sleep(1)
            
            #from WebDriver to Beautiful Soap 
            button_more_parse= soupParser1.find('div', {'class': ''+class_after_button_more+''}) #conteiner menu button more Beautiful Soap   

            #find Menu list conteiner menu button more - Beautiful Soap 
            lista_li_button_more_parse= button_more_parse.find_all_next('li')

            strUrl=""
            stop=False
            #elenco menu button more - Beautiful Soap 
            for element_li_button_more_parse in lista_li_button_more_parse:
                if(stop):
                        break
                try: 
                    list_text_span= element_li_button_more_parse.find_all_next('span', {'aria-hidden' :'true', 'class':'display-flex t-normal flex-1'}) #testo elenco button more - Beautiful Soap 
                    
                    #elenco dello span dell'elenco button more - Beautiful Soap 
                    for element_text_span in list_text_span:
                        if(stop):
                            break
                        try:
                            text_span= element_text_span.get_text() #testo span - Beautiful Soap 
                            
                            if(text_span=='Save to PDF'):
                                div_download_pdf = element_text_span.find_parent('div', {'role':"button", 'tabindex':"0"}) #div contenente download pdf - Beautiful Soap 
                                id_div_download_pdf_soap = div_download_pdf.get("id") #id del div contenente download pdf - Beautiful Soap 
                                
                                #from beautiful soap to web driver
                                div_download_pdf_webdriver = self.driver.find_element_by_id(id_div_download_pdf_soap)
                                id_div_download_pdf_webdriver = div_download_pdf_webdriver.get_attribute("id")

                                #per ogni bottone more nella pagine
                                for element_button_more in list_button_more:
                                    if(stop):
                                        break
                                    #ricavo l'id
                                    id_button_more = element_button_more.get_attribute("id")                                    

                                    #clicco il pulsante, è possibile cliccare solo 1 tra tutti, che è proprio quello che ci interessa
                                    ActionChains(self.driver)\
                                            .click(element_button_more)\
                                            .perform()
                                    sleep(1)
                                    #clicco "Save as PDF", aprirà una nuova tab col CV
                                    ActionChains(self.driver)\
                                            .click(div_download_pdf_webdriver)\
                                            .perform()
                                    sleep(1)

                                    # Switch to the newly opened tab
                                    try:
                                        self.driver.switch_to.window(self.driver.window_handles[1])
                                        strUrl = self.driver.current_url
                                        if(strUrl!='' or strUrl!=' '):
                                            stop=True
                                            sleep(1)
                                            self.driver.switch_to.window(self.driver.window_handles[0])
                                    except:
                                        continue
                                    
                        except:
                            continue
                except:
                    continue
            sleep(1)
            path_Curriculum = (strUrl.replace("file:///" , "")).replace("/", "\\")

            dest_path=".\\Potential_target_image\\" + full_name+"\\Curriculum " + full_name+ ".pdf"
            shutil.move(path_Curriculum, dest_path)      
          
        except Exception as e:
            #traceback.print_exc()
            #print(e)
            pass
        

        ActionChains(self.driver).move_to_element(self.driver.find_element_by_xpath('//*[@class="ember-view link-without-visited-state cursor-pointer text-heading-small inline-block break-words"]')).click().perform()
        sleep(3)

        # carico la sezione delle Contact-info
        title_Contact_Info = self.driver.find_elements_by_xpath('//*[@class="pv-contact-info__header t-16 t-black t-bold"]')
        for e in title_Contact_Info:
            #estrapolo le informazioni circa Sito Web
            if(e.text == 'Websites'):
                sito=[]
                tipo_Sito=[]
                info_Sito=[]
                try:
                    elenco = e.find_element_by_xpath('//*[@class="list-style-none"]')
                    elenco1 = elenco.find_elements_by_tag_name('li')
                    temp1 = elenco1[0].find_elements_by_xpath('//*[@class="pv-contact-info__contact-link link-without-visited-state"]')
                    for t in temp1:
                        sito.append(str(t.text.strip()))

                    temp2 = elenco1[0].find_elements_by_xpath('//*[@class="t-14 t-black--light t-normal"]')

                    for t1 in temp2:
                        tipo_Sito.append(str(t1.text.strip()))
                        
                    for numero in range(len(sito)):
                        info_Sito.append(sito[numero] + " "+ tipo_Sito[numero])
                except Exception as e:
                    #print(e)
                    continue

                if info_Sito.count !=0:
                    info["Sito Web"]= " - ".join(info_Sito)
                else:
                    info["Sito Web"]= ""
            
            #estrapolo le informazioni circa Cellulare
            elif e.text == 'Phone':
                cellulare=""
                tipo_cellulare=""
                info_cellulare=[]

                try:
                    temp1 = e.find_element_by_xpath('//*[@class="t-14 t-black t-normal"]')
                    cellulare = str(temp1.text.strip())

                    temp2 = e.find_element_by_xpath('//*[@class="t-14 t-black--light t-normal"]')
                    tipo_cellulare = str(temp2.text.strip())

                    info_cellulare.append(cellulare + " "+ tipo_cellulare)
                except Exception as e:
                    #print(e)
                    continue 

                if info_cellulare.count !=0:
                    info["Cellulare"]= " - ".join(info_cellulare)
                else:
                    info["Cellulare"]= ""

            #estrapolo le informazioni circa Indirizzo  
            elif e.text == 'Address':
                indirizzo=""  
                try:
                    temp1 = e.find_element_by_xpath('//*[@class="pv-contact-info__contact-link link-without-visited-state t-14"]')
                    indirizzo = str(temp1.text.strip())
                except Exception as e:
                    #print(e)
                    continue
                info["Indirizzo"] = indirizzo

            #estrapolo le informazioni circa Email
            elif e.text == 'Email':
                email=""
                try:
                    temp1 = e.find_element_by_xpath('//*[@class="pv-contact-info__contact-link link-without-visited-state t-14"]')
                    email = str(temp1.text.strip())
                except Exception as e:
                    #print(e)
                    continue     
                info["Email"] = email

            #estrapolo le informazioni circa Messaggistica istantanea
            elif e.text == 'IM':
                im=[]
                tipo_IM=[]
                info_IM=[]
                try:
                    elenco = e.find_element_by_xpath('//*[@class="list-style-none"]')
                    elenco1 = elenco.find_elements_by_tag_name('li')

                    temp1 = elenco1[0].find_elements_by_xpath('//*[@class="pv-contact-info__contact-item t-14 t-black t-normal"]')
                    for t in temp1:
                        im.append(str(t.text.strip()))

                    temp2 = elenco1[0].find_elements_by_xpath('//*[@class="t-14 t-black--light t-normal"]')

                    for t1 in temp2:
                        tipo_IM.append(str(t1.text.strip()))
                        
                    for numero in range(len(im)):
                        info_IM.append(im[numero] + " "+ tipo_IM[numero])
                except Exception as e:
                    #print(e)
                    continue    

                if info_IM.count !=0:
                    info["Messaggistica"]= " - ".join(info_IM)
                else:
                    info["Messaggistica"]= ""

            #estrapolo le informazioni circa Compleanno
            elif e.text == 'Birthday':
                compleanno=""
                try:
                    temp1 = e.find_element_by_xpath('//*[@class="pv-contact-info__contact-item t-14 t-black t-normal"]')
                    compleanno = str(temp1.text.strip())
                except Exception as e:
                    #print(e)
                    continue

                info["Compleanno"] = compleanno
        return info

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