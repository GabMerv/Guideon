### Guideon

## Introduction

Guideon est une intelligence artificielle tchatbot entièrement codée en Python avec les frameworks de tensorflow. Elle permet de faciliter la vie au quotidient avec certaines taches qui sont automatisées.
On retrouve:
.l'envoie d'un email
.l'envoie d'un message
.l'ouverture de certaines applications
. ...

## Mise en place

téléchargez l'entièreté du projet git et exécuter le fichier **main.py** (vérifier le fichier requirements.txt)
remplissez le fichier de configuration **datas.json**

## Changer la base de donnée

Dans le fichier **intents.json** vous pouvez ajouter des phrases sous la forme:
```json
{"tag": "tag",
         "patterns": ["phrase exemple 1", "phrase exemple 2"],
         "responses": ["Phrase réponse 1", "Phrase réponse 2"],
         "context_set": ""
},
```
De la même manière, vous pouvez supprimer des éléments (par exemple le tag wikipedia pour enlever la possibilité de rechercher sur wikipedia)

Pour des actions plus personalisées, vous pouvez rajouter une condition dans le fichier **main.py** de la forme:
```py
if tag == "ennuis":
   webbrowser.open_new("https://www.youtube.com/watch?v=RLQiAqc1MI8")
```
Le tag doit être celui ajouté dans le fichier json
De cette manière, vous pouvez ajouter plusieurs applications à ouvrir avec les commandes

Pour plus de précision, vous pouvez ajouter d'autres phrases exemples / phrases réponses dans les autres tag du fichier **intents.json**

- BicorneCosmique