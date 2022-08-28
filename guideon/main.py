# Voix (si vous êtes sous windows)
#import win32com.client as w

# IA
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf

# Emails & messages
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

#Check phone nb
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# Utilitaire
import random
import json
import pickle
import os
from time import sleep
import webbrowser
from glob import glob
import sys
import wikipedia
import datetime

def clear():
   os.system("cls" if os.name == "nt" else "clear")


# Récupérer les arguments dans le lancement de la commande python
# et savoir si on demande d'entrainer l'IA
try:
   train = sys.argv[1]
except:
   train = False

# Variable du chemin d'accès du dossier
path_before = os.getcwd()

# On récupère toutes les données
with open(path_before + "\\datas.json", "r", encoding='utf-8') as file:
   infos = json.load(file)

with open(path_before + "\\intents.json", "r", encoding='utf-8') as file:
   data = json.load(file)

#Variables pour messages / mails / etc
client = Client(infos["sid"], infos["author_token"])
stemmer = LancasterStemmer()
#Voix si sous windows
#speak = w.Dispatch("SAPI.SpVoice")
sid = infos["sid"]
auth_token = infos["author_token"]
sender = infos["email"]
password = infos["code_email"]

# Wikipedia
wikipedia.set_lang("fr")

#Récupérer les données pré-existantes
if not train:
   path = path_before + "/save/data.pickle"

   with open(path, 'rb') as f:
      words, labels, training, output = pickle.load(f)

else:
   #Entrainement de l'IA
   words = []
   labels = []
   docs_x = []
   docs_y = []

   for intent in data["intents"]:
      for pattern in intent["patterns"]:
         wrds = nltk.word_tokenize(pattern)
         words.extend(wrds)
         docs_x.append(wrds)
         docs_y.append(intent["tag"])

      if intent["tag"] not in labels:
         labels.append(intent["tag"])

   words = [stemmer.stem(w.lower()) for w in words if  w not in "?"]
   words = sorted(list(set(words)))

   labels = sorted(labels)

   training = []
   output = []

   output_empty = [0 for _ in range(len(labels))]

   for x, doc in enumerate(docs_x):
      bag = []

      wrds = [stemmer.stem(w) for w in doc]

      for w in words:
         if w in wrds:
            bag.append(1)
         else:
            bag.append(0)

      output_row = output_empty[:]
      output_row[labels.index(docs_y[x])] = 1

      training.append(bag)
      output.append(output_row)

   training = np.array(training)
   output = np.array(output)

   path = path_before + "/save/data.pickle"
   with open(path, 'wb') as f:
      pickle.dump((words, labels, training, output), f)

# Modèle IA
tf.compat.v1.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)
model = tflearn.DNN(net)

if train:
   model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
   path = path_before + '/save/model.tflearn'
   model.save(path)
else:
   path = path_before + '\\save\\model.tflearn'
   model.load(path)

def bag_of_words(s, words):
   bag = [0 for _ in range(len(words))]
   s_words = nltk.word_tokenize(s)

   s_words = [stemmer.stem(word.lower()) for word in s_words]
   for se in s_words:
      for i, w  in enumerate(words):
         if w == se:
            bag[i] = 1
   return np.array(bag)

def start_app(path):
   sleep(2)
   os.system("start {}".format(path))
   clear()

def chat(data):
   clear()
   results = model.predict([bag_of_words("Bonjour", words)])[0]
   results_index = np.argmax(results)
   clear()
   print("Commence à parler avec le bot (écris quit pour fermer le programme)!")
   while True:
      inp = input("Vous -> ")

      char_toChange = "     eecau  "
      for i, char in enumerate("!?;.,éèçàù-'"):

         inp = inp.replace(char, char_toChange[i])
      inp = inp.lower()

      if inp.lower() == "quit":
         print("Guideon -> Au revoir!")
         #Voix si sous windows
         #speak.Speak("Au revoir")

         break
      else:
         results = model.predict([bag_of_words(inp, words)])[0]
         results_index = np.argmax(results)
         tag = labels[results_index]

         s_tag = None

         if results[results_index]> 0.7:

            for tg in data["intents"]:
               if tg["tag"] == tag:
                  responses = tg["responses"]
                  s_tag = tag

                  break
            reponse = random.choice(responses)
            #Voix si sous windows
            #speak.Speak(reponse)

            print("Guideon -> " + reponse)


            if tag == "msg":
               if input("Validation de l'action (y/n): ") == "y":
                  resp = client.messages.create(body=input("Entrer le texte du message: "), from_=infos["twilio_nb"], to=input("A qui voulez vous envoyer ce message?: "))
                  print("Message envoyé!")

            if tag == "mail":
               if input("Validation de l'action (y/n): ") == "y":
                  msg = EmailMessage()
                  msg['to'] = input("Mail de destinataire: ")
                  msg['subject'] = input("Veuillez entrer l'objet du message: ")
                  msg['from'] = sender
                  msg.set_content(input("Veuillez entrer votre message: "))
                  with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                      smtp.login(sender,password)

                      smtp.send_message(msg)
                      print("Message envoyé!")

            if tag == "partir":
               break

            if tag == "whatsapp":
               start_app(infos["links"]["whatsapp"])

            if tag == "discord":
               start_app(infos["links"]["discord"])

            if tag == "teams":
               start_app(infos["links"]["teams"])

            if tag == "python":
               start_app("python")

            if tag == "check_phone":
               print("-"*10)
               mobileNo = input()
               mobileNo = phonenumbers.parse(mobileNo)

               if phonenumbers.is_valid_number(mobileNo):
                  print("Numéro valide!")
                  print(timezone.time_zones_for_number(mobileNo))
                  print("Operateur: " + carrier.name_for_number(mobileNo, "en"))
                  print(geocoder.description_for_number(mobileNo, "en"))

               else:
                  print("Invalide!")
               print("-"*10)

            if tag == "setup":
               for app in infos["links"]["setup"]:
                  start_app(app)

            if tag == "yt":
               src = input("")

               if src.startswith("http") or src.startswith("www."):
                  webbrowser.open_new(src)

               else:
                  webbrowser.open_new("https://www.youtube.com/results?search_query=" + src.replace(" ", "+"))

            if tag == "shodan":
               src = input("")

               if src.startswith("http") or src.startswith("www."):
                  webbrowser.open_new(src)

               else:
                  webbrowser.open_new("https://www.shodan.io/search?query=" + src.replace(" ", "+"))

            #Voix si sous windows
            #if tag == "repeat":
               #speak.Speak(input())

            if tag == "ennuis":
               webbrowser.open_new("https://www.youtube.com/watch?v=RLQiAqc1MI8")

            if tag == "heure":
               heure = datetime.datetime.now()
               print("Guideon -> En vrai voilà l'heure:")
               #Voix si sous windows
               #speak.Speak("En vrai voilà l'heure:")
               print("Guideon -> {}".format(heure))

            if tag == "train":
               if input("(y/n) => ") == "y":
                  #Voix si sous windows
                  #speak.Speak("Go! je lance mon programme")
                  os.system("python {}\\main.py True".format(path_before))
                  sys.exit()

            if tag == "music":
               path = path_before + "\\music\\*"
               doss = glob(path)
               for i, dossier in enumerate(doss):
                  name = dossier.split("\\")[-1]
                  name = name.split(".")[0]
                  print("(" + str(i) + ") " + name)

               index = int(input("Quelle musique jouer?: "))
               try:
                  path_mus = doss[index]
                  print("Lecture de: " + doss[index])
                  os.system("start " + path_mus)
               except:
                  pass

            if tag == "wiki":
               try:
                  inp = input("")
                  txt = wikipedia.summary(inp)
                  print(txt)
                  #Voix si sous windows
                  #if input("Voulez vous que je lise le texte? (y/n)") == "y":

                     #speak.Speak(txt)
               except:
                  print("Erreur...")

            if tag == "calcul":
               try:
                  print(eval(input()))
               except:
                  pass

            if tag == "search":
               src = input("Veuillez entrer le sujet de votre recherche: ")

               if src.startswith("http") or src.startswith("www."):
                  webbrowser.open_new(src)

               else:
                  webbrowser.open_new("https://www.google.fr/search?q=" + src.replace(" ", "+"))

         else:
            print("Guideon -> Je ne comprends pas...")
            #Voix si sous windows
            #speak.Speak("Je ne comprends pas...")

            # Ajouter ces lignes de code pour rechercher les éléments que Guideon ne comprend pas

            #print("Guideon -> Voulez vous que je recherche cette information?")
            #speak.Speak("Voulez vous que je recherche cette information?")
            #if input("(y/n) => ") == "y":
            #   webbrowser.open_new("https://www.google.fr/search?q=" + inp.replace(" ", "+"))


try:
   chat(data)
except:
   print("Guideon -> Erreur lors de l'exécution de la commande...")
