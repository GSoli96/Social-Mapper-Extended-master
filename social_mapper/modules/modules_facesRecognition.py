from fileinput import close
from deepface import DeepFace
import deepface
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import face_recognition
from PIL import Image
import numpy
from time import sleep
import traceback

global metrics
metrics = ["cosine", "euclidean", "euclidean_l2"]
global models
models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]
global backends
backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']
# thresholds = {
                # 'VGG-Face': {'cosine': 0.40, 'euclidean': 0.60, 'euclidean_l2': 0.86},
                # 'Facenet':  {'cosine': 0.40, 'euclidean': 10, 'euclidean_l2': 0.80},
                # 'Facenet512':  {'cosine': 0.30, 'euclidean': 23.56, 'euclidean_l2': 1.04},
                # 'ArcFace':  {'cosine': 0.68, 'euclidean': 4.15, 'euclidean_l2': 1.13},
                # 'Dlib': 	{'cosine': 0.07, 'euclidean': 0.6, 'euclidean_l2': 0.4}
                # 'SFace': 	{'cosine': 0.5932763306134152, 'euclidean': 10.734038121282206, 'euclidean_l2': 1.055836701022614},
                # 'OpenFace': {'cosine': 0.10, 'euclidean': 0.55, 'euclidean_l2': 0.55},
                # 'DeepFace': {'cosine': 0.23, 'euclidean': 64, 'euclidean_l2': 0.64},
                # 'DeepID': 	{'cosine': 0.015, 'euclidean': 45, 'euclidean_l2': 0.17}

class modules_facesRecognition():
   
    # 
    #Librearia: face_recognition
    # 

    #
    # Metodo che effettua la distanza tra una lista di immagini confermate della persona e l'immagine estrapolata dal social
    #
    # @param socia_img Stringa che rappresenta la foto della persona sui social trovata 
    # @param threshold Float sogli di matching per la face recognition
    # @param person Persona da identificare tramite Face_Recognition
    # @param image_link Stringa Contiene il link dell'immagine del social
    # 
    # @return flag Bool valore booleano, True se c'è un matching, falso altrimenti
    #
    # typeFacesRecognition = 1 
    def facesDistance_FR(self,socia_img,threshold, person,image_link):
        try:
            listResult=[]
            outputfilename = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"

            list_img = person.person_target_images_link

            #carico l'immagine social scaricata sul dispositivo
            potential_image = face_recognition.load_image_file(socia_img) 
            potential_target_encoding = face_recognition.face_encodings(potential_image)[0]

            countr=0
            #per ogni foto già confermata di altro social della persona
            for person_link in list_img:
                try:
                    #carico l'immagine
                    target_image = face_recognition.load_image_file(person_link)
                    target_encoding= face_recognition.face_encodings(target_image)[0]

                    #confronto le due immagini
                    resultRecognition = (face_recognition.face_distance([potential_target_encoding], target_encoding))
                    
                    #controllo se l'immagine è minore o maggiore della soglia impostata
                    if(resultRecognition < threshold):
                        result = numpy.array_str(resultRecognition)
                        listResult.append((True,((result.replace('[', '')).replace(']', '')),  person_link,image_link))
                    elif(resultRecognition >= threshold): 
                        result = numpy.array_str(resultRecognition)
                        listResult.append((False,((result.replace('[', '')).replace(']', '')), person_link, image_link))

                except Exception as e:
                    continue 
                countr=countr+1

            tmp=""
            
            #per ogni confronto effettuato, salvo i dati in un file
            for tupla in listResult:
                try:
                    tmp = tmp+ str(tupla[0]) + " - "+ str(tupla[1])+" - "+ str(tupla[2])+" - "+str(tupla[3])+"\n"
                except Exception as e:
                    #traceback.print_exc()
                    #print(e)
                    continue
              
            with open(outputfilename, "a") as filewriter:
                filewriter.write(tmp)
            
            flag=False

            #per ogni cofronto effettuato, se uno ha avuto esito positivo allora persona identificata
            for tupla in listResult:
                if(tupla[0]):
                    flag=True
                    break
            #scrivo nel file il risultato
            if(flag):
                with open(outputfilename, "a") as filewriter:
                    filewriter.write("Result: True\n\n")
            elif(not flag):
                with open(outputfilename, "a") as filewriter:
                    filewriter.write("Result: False\n\n")
            return flag
             
        except Exception as e:
            # traceback.print_exc()
            # print(e)
            return False



    # 
    #Librearia: deepface
    # 

    #Deepface è un pacchetto di riconoscimento facciale ibrido . Attualmente racchiude molti modelli di riconoscimento facciale all'avanguardia
    #La configurazione predefinita utilizza la somiglianza del coseno.
    #La forma euclidea L2 è più stabile del coseno e della distanza euclidea regolare, sulla base degli esperimenti.

    #
    # Metodo che effettua un confronto a maggioranza tra una lista di immagini confermate della persona e l'immagine estrapolata dal social
    #
    # @param socia_img Stringa che rappresenta la foto della persona sui social trovata 
    # @param person Persona da identificare tramite Face_Recognition
    # @param image_link Stringa Contiene il link dell'immagine del social
    # @return boolean valore booleano che identifica, True se la foto social matcha con quelle già confermate in precedenza
    #                                                 False se le foto social non matcha con quelle già confermate in precedenza
    # typeFacesRecognition = 2
    def deepFace_majority(self, socia_img,person,image_link):
        
        try:
            list_img = person.person_target_images_link
            listResult=[]
            outputfilename = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"
            #list_img lista di immagini della persona cercata che hanno matchato in precedenza
            
            for img in list_img:
                
                final_result = []
                count = 0
                #per ogni modello della libreria 
                for model in models:
                    count = count+1
                    #verifico se le due immagini contengono la stessa persona
                    result= DeepFace.verify(img1_path = img, img2_path = socia_img, model_name = model, distance_metric=metrics[1], enforce_detection=False,prog_bar=False,detector_backend = backends[0])
                    res= result['verified']
                    dist= result['distance']
                    maxThreshold= result['threshold']

                    final_result.insert(count-1,res)
                    listResult.append((res, dist, maxThreshold, model , img, image_link))
                    #scrivo in un file il risultato
                    with open(outputfilename, "a") as filewriter:
                        filewriter.write(str(res) + " - "+ str(dist)+" - "+ str(maxThreshold)+" - "+str(model)+ " - " +str(img)+" - "+str(image_link)+"\n")
                #se la maggioranza dei modelli ha esito positivo allora persona identificata
                if sum(final_result)>=((count)/2):
                    with open(outputfilename, "a") as filewriter:
                        filewriter.write("Result: True\n\n")
                    return True
                else:
                    with open(outputfilename, "a") as filewriter:
                        filewriter.write("Result: False\n\n")
                    continue

        except Exception as e:
            #traceback.print_exc()
            #print(e)
            return False    
    
    
    # 
    #Librearia: face_recognition - PIL - deepface
    #
         
    #
    # Metodo che effettua il ritaglio delle facce in ogni immagine di una lista di immagini confermate della persona e
    # calcola le distanze con l'immagine estrapolata dal social
    #
    # @param socia_img Stringa che rappresenta la foto della persona sui social trovata 
    # @param threshold Float sogli di matching per la face recognition
    # @param person Persona da identificare tramite Face_Recognition
    # @param image_link Stringa Contiene il link dell'immagine del social
    #
    # @return results numpy ndarray contenete le distanze tra ogni faccia nella lista e la foto presa dai social
    #
    # typeFacesRecognition = 3
    # def cut_Recognition(self,socia_img, threshold, person,image_link):
    #     try:
    #         list_img = person.person_target_images_link
    #         name = person.full_name
    #         self.face_location(socia_img,'.\\temp-targets\\Profile_face\\'+name)# facce social image
            
    #         outputfilename = ".\\Potential_target_image\\" + person.full_name+"\\InfoRecognition.txt"
    #         listResult=[]
            
        
    #         for person_link in list_img:
                
    #             self.face_location(person_link,'.\\temp-targets\\Original_face\\'+name)# facce potential image

    #             if(len(os.listdir('.\\temp-targets\\Original_face\\'))==0): # facce potential image
    #                 potential_path= '.\\Potential_target_image\\'+ name +'\\'
                    
    #                 if(len(os.listdir('.\\temp-targets\\Profile_face\\'))==0):# facce social image
                        

    #                     df = DeepFace.find(img_path = socia_img, db_path = potential_path ,model_name = models[0],distance_metric = metrics[1],detector_backend = backends[0],enforce_detection=False)
                        
    #                     for result in df.values.tolist():
    #                         if (float(result[1]) <= threshold):
    #                             listResult.append((True,str(result[1]), person_link, image_link))
    #                         else:
    #                             listResult.append((False,str(result[1]), person_link, image_link))                    

    #                 elif (len(os.listdir('.\\temp-targets\\Profile_face\\'))!=0):
                        
    #                     social_path= '.\\temp-targets\\Profile_face\\'

    #                     for face_profile in os.listdir(social_path): 
    #                         # per ogni faccia trovata nella foto profilo social
    #                         # trova somiglianze tra la faccia e l immagine della persona
    #                         df = DeepFace.find(img_path = social_path+face_profile, db_path = potential_path ,model_name = models[0],distance_metric = metrics[1],detector_backend = backends[0],enforce_detection=False)
                            
    #                         for result in df.values.tolist():
    #                             if (float(result[1]) <= threshold):
    #                                 listResult.append((True,str(result[1]), person_link, image_link))
    #                             else:
    #                                 listResult.append((False,str(result[1]), person_link, image_link))
                        

    #             elif(len(os.listdir('.\\temp-targets\\Original_face\\'))!=0):  # facce potential image
                    
    #                 potential_path = '.\\temp-targets\\Original_face\\'

    #                 if(len(os.listdir('.\\temp-targets\\Profile_face\\'))==0): # facce social image
                        
                        
    #                     df = DeepFace.find(img_path = socia_img, db_path = potential_path ,model_name = models[0],distance_metric = metrics[1],detector_backend = backends[0],enforce_detection=False)
                        
    #                     for result in df.values.tolist():
    #                         if (float(result[1]) <= threshold):
    #                             listResult.append((True,str(result[1]), person_link, image_link))
    #                         else:
    #                             listResult.append((False,str(result[1]), person_link, image_link))
                        
                        
    #                 elif (len(os.listdir('.\\temp-targets\\Profile_face\\'))!=0):
                        
    #                     social_path= '.\\temp-targets\\Profile_face\\'
    #                     potential_path= '.\\Potential_target_image\\'+ name +'\\'
                        
    #                     for face_profile in os.listdir(social_path):
    #                         df = DeepFace.find(img_path = social_path+face_profile, db_path = potential_path ,model_name = models[0],distance_metric = metrics[1],detector_backend = backends[0],enforce_detection=False)
                            
    #                         for result in df.values.tolist():
    #                             if (float(result[1]) <= threshold):
    #                                 listResult.append((True,str(result[1]), person_link, image_link))
    #                             else:
    #                                 listResult.append((False,str(result[1]), person_link, image_link))  
                
    #             print('listResult: ' + str(len(listResult)))
    #             print(listResult)
                   

            
    #         tmp=""
            
    #         for tupla in listResult:
    #             try:
    #                 tmp = tmp + str(tupla[0]) + " - "+ str(tupla[1])+" - "+ str(tupla[2])+" - "+str(tupla[3])+"\n"
    #             except Exception as e:
    #                 traceback.print_exc()
    #                 print(e)
    #                 continue
    #         print("SI10\n"+tmp)

    #         match=0
    #         notMatch=0
    #         print("match: " + str(match)+ " notMatch: " + str(notMatch))
    #         for tupla in listResult:
    #             if(tupla[0]==True):
    #                 match=match+1
    #             elif(tupla[0]!=True):
    #                 notMatch=notMatch+1

    #         print("match: " + str(match)+ " notMatch: " + str(notMatch))

    #         if(match>=notMatch):
    #             with open(outputfilename, "a") as filewriter:
                
    #                 filewriter.write(tmp+"\nResult: True\n\n")
    #             return True
    #         elif(match<notMatch):
    #             with open(outputfilename, "a") as filewriter:
                
    #                 filewriter.write(tmp+"\nResult: False\n\n")
    #             return False 
    #         print("QUI")                   
                    
    #     except Exception as e:
    #         traceback.print_exc()
    #         print(e)
    #         return False





    #
    # Metodo che effettua la distanza tra una lista di immagini confermate della persona e l'immagine estrapolata dal social
    #
    # @param list_img Lista Contiene le path delle immagini già confermate della persona da trovare
    # @param socia_img Stringa che rappresenta la foto della persona sui social trovata 
    #
    # @return results numpy ndarray contenete le distanze tra ogni faccia nella lista e la foto presa dai social
    #
    # typeFacesRecognition = 4 
    # def face_recognition(self, path,threshold, person,image_link):
    #     try:
    #         final_result=[]
    #         list_result=[]
    #         count=0
    #         #La configurazione predefinita utilizza il modello VGG-Face.
    #         #Facenet512 è il migliore
    #         for file in os.listdir(path):
    #             for model in models:
    #                 count = count+1
    #                 df = DeepFace.find(img_path = path+"\\"+ file, db_path = '.\\temp-targets\\' ,distance_metric = metrics[1], model_name = model,detector_backend = backends[0],enforce_detection=False,prog_bar=False)
    #                 final_result=df.values.tolist()
    #                 if(len(df.values.tolist())!=0):
    #                     list_result.insert(count-1, final_result)
    #                 final_result=[]
    #             sys.stdout.flush()
            
            
            
    #         for file in os.listdir('.\\temp-targets\\'):
    #             if "representations_" in file:
    #                 os.remove('.\\temp-targets\\'+ file)
            
    #         i=0
    #         dist=0
            

    #         if(len(list_result)!=0):
    #             for list in list_result:
    #                 for element in list:
    #                     tmp_dist=float(element[1])  
                        
                        
    #                     if i==0:
    #                         dist=tmp_dist
                           
    #                     else:
    #                         if tmp_dist<dist:
    #                             dist=tmp_dist
    #                     i=i+1
                
    #             if(dist<=threshold):
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             return False
            
    #     except Exception as e:
    #         # traceback.print_exc()
    #         # print(e)
    #         return False


            
    # # typeFacesRecognition = 5
    # def face_majority(self,socia_img, threshold,person,image_link):
    #     list_img = person.person_target_images_link
    #     name = person.full_name
    #     try:
    #     # thresholds = {
    #             # 'VGG-Face': {'cosine': 0.40, 'euclidean': 0.60, 'euclidean_l2': 0.86},
    #             # 'Facenet':  {'cosine': 0.40, 'euclidean': 10, 'euclidean_l2': 0.80},
    #             # 'Facenet512':  {'cosine': 0.30, 'euclidean': 23.56, 'euclidean_l2': 1.04},
    #             # 'ArcFace':  {'cosine': 0.68, 'euclidean': 4.15, 'euclidean_l2': 1.13},
    #             # 'Dlib': 	{'cosine': 0.07, 'euclidean': 0.6, 'euclidean_l2': 0.4}
    #             # 'SFace': 	{'cosine': 0.5932763306134152, 'euclidean': 10.734038121282206, 'euclidean_l2': 1.055836701022614},
    #             # 'OpenFace': {'cosine': 0.10, 'euclidean': 0.55, 'euclidean_l2': 0.55},
    #             # 'DeepFace': {'cosine': 0.23, 'euclidean': 64, 'euclidean_l2': 0.64},
    #             # 'DeepID': 	{'cosine': 0.015, 'euclidean': 45, 'euclidean_l2': 0.17}
            
        
    #         self.face_location(socia_img,'.\\temp-targets\\Profile_face\\'+name)# facce social image

        
    #         for person_link in list_img:
                
    #             self.face_location(person_link,'.\\temp-targets\\Original_face\\'+name)# facce potential image

    #             if(len(os.listdir('.\\temp-targets\\Original_face\\'))==0): # facce potential image
    #                 potential_path= '.\\Potential_target_image\\'+ name +'\\'

    #                 if(len(os.listdir('.\\temp-targets\\Profile_face\\'))==0):# facce social image
                    
    #                     if(self.deepFace_majority(list_img=list_img, socia_img= socia_img)):
    #                         return True
                       

    #                 elif (len(os.listdir('.\\temp-targets\\Profile_face\\'))!=0):
                        
    #                     social_path= '.\\temp-targets\\Profile_face\\'
    #                     deep_result=[]
    #                     count=0

    #                     for face_profile in os.listdir(social_path):
    #                         deep_result.insert(count,self.deepFace_majority(list_img=list_img, socia_img= social_path+ "\\"+face_profile))
    #                         count=count+1
                             
    #                     if sum(deep_result)>=((count-1)/2):
    #                         return True
                            

    #             elif(len(os.listdir('.\\temp-targets\\Original_face\\'))!=0):  # facce potential image
    #                 potential_path = '.\\temp-targets\\Original_face\\'

    #                 if(len(os.listdir('.\\temp-targets\\Profile_face\\'))==0): # facce social image
    #                     list_img=[]

    #                     for potential_img in os.listdir(potential_path):
    #                         list_img.append(potential_path+ "\\"+potential_img)
                            
    #                     if self.deepFace_majority(list_img=list_img, socia_img= socia_img):
    #                         return True
                         
                        
    #                 elif (len(os.listdir('.\\temp-targets\\Profile_face\\'))!=0):
    #                     deep_result=[]
    #                     img=[]
    #                     count=0
    #                     social_path= '.\\temp-targets\\Profile_face\\'       
                                
    #                     for potential_img in os.listdir(potential_path):
    #                         img.append(potential_path+ "\\"+potential_img)

    #                     for face_profile in os.listdir(social_path):
    #                         deep_result.insert(count,self.deepFace_majority(list_img=img, socia_img= social_path+ "\\"+face_profile))
    #                         count=count+1
                             
    #                     if sum(deep_result)>=((count-1)/2):
    #                         return True
    #         return False
            
    #     except Exception as e:
    #         # traceback.print_exc()
    #         # print(e)
    #         return False
    

    # # typeFacesRecognition = 3  # typeFacesRecognition = 5 
    # def face_location(self,person_link,path):
    #     try:
    #         target_image_folder = face_recognition.load_image_file(person_link)
            
    #         face_locations_folder = face_recognition.face_locations(target_image_folder)
            
    #         if(len(face_locations_folder)!=0):
                
    #             cont_face=0
    #             for face_location_folder in face_locations_folder:
                    
    #                 top, right, bottom, left = face_location_folder
                                
    #                 face_image_folder = target_image_folder[top:bottom, left:right]
                            
    #                 pil_image = Image.fromarray(face_image_folder)
                                
    #                 pil_image.save(path+str(cont_face)+'.jpg')
                            
    #                 cont_face=cont_face+1
    #         else:
    #             if '.\\temp-targets\\Profile_face\\' in path:

    #                 for file in os.listdir('.\\temp-targets\\Profile_face\\'):

    #                     os.remove('.\\temp-targets\\Profile_face\\'+file)
            
    #     except Exception as e:
    #         # traceback.print_exc()
    #         # print(e)
    #         return False


