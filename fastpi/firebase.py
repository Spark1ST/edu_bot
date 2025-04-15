# import firebase_admin
# from firebase_admin import credentials, firestore, auth

# def initialize_firebase():
#     if not firebase_admin._apps:
#         cred = credentials.Certificate("..\data\grad-51668-firebase-adminsdk-fbsvc-b04feff7eb.json")
#         firebase_admin.initialize_app(cred)
    
#     return {
#         'auth': auth,
#         'db': firestore.client()
#     }

# firebase = initialize_firebase()
