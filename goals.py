import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#https://firebase.google.com/docs/firestore/quickstart#python_7
# Use a service account
cred = credentials.Certificate('/home/ls/Desktop/code/GitHub/telegrambot-learning/sa.json')
firebase_admin.initialize_app(cred)

firebase_db = firestore.client()


def get_goals_list():
    return 'eat'

collectionRef = firebase_db.collection('users')#collectionreference
    
all_users = collectionRef.stream()

print(all_users)