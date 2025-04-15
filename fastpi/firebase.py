import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit as st

def initialize_firebase():
    if not firebase_admin._apps:
        firebase_key_str = "{\"type\": \"service_account\", \"project_id\": \"grad-51668\", \"private_key_id\": \"e46f5545a19ed35d3d106e9be8573718f89cc9fe\", \"private_key\": \"-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCyBFE1hvLPnG7l\\nL6vTHIfr+aCJAR1TG0e6tNmJEU28rVz/Zu5MtdNw7fM17wTRBUQFhyvOe8AJin/i\\n+nlAWHNWjvNW4PBk7udAM5D9M9VqWEWekilwC4drxfm7MnDTH3tEnJZaNvnJsW/q\\nIjolDCw12fLEKJMOzmSOGh7NsNU4WJIB6vwIyk8byfPYA/2AqK2jmaevA+9dGfRP\\nEm1lHLq2dEwJ8NjZjUjKsquYB1sy2lNz+mtaFQ90XXVfhmjd0qnb2F61pC4r1LXp\\nMeJV3AdP3KMvcILiVwVr34GKBfsih6Yg6tBLH2m292pHqel69pNdWnZGLzv6AlJo\\nmFdT37upAgMBAAECgf8PKewScbrl7p7VG1pzO2aSzXl/SWeQQRcA6qbXSROBwdoE\\nUDeNy29AJqew/vnKDndRO2mxUt8XZVTWve3WLVWOjOph580eEbum7dTXjiciqtDO\\n/6olDNZcQ3g5pZU2w8wcSS6/tOlSKshDiXJ79Werxe22k4QKntXJOV7sLFtDHPUl\\n3PTnngSml8NrmBQSnurCKqtcTZrcgZsajDdcCWlGDWAy7Xw//3UVF/KNUX471e7j\\nsje6wzZ8uCKdakJFaOEqmKRGlUfcC0nUyf//wmoYvUMskW8uN6yYcx6LlvrjFLgb\\nsbx0/W0QkdLAEfc6oxEPFYk0tHvAEmNnCM8+gzECgYEA8KujjM5lJAuRRY+FtZtJ\\nDeQwCPCEk8j3Hr9UCxpMWEK5ZS5IVDoYGQyA0zzuDL1fwK47lN8XXCSrzpCnZd2j\\nVifgO8m5jd4tSoaIsHhDPMbiuO+eLoCqgcGFh7ecvf9xmExZHMpkiWV66qKBAjlz\\nTLV0vtg/+HXmg826pPUjjtECgYEAvVsNPnWxLclqYY5WAitW8IpE+yOsL6Arwbo6\\n9h/SrPtt6JQPed2v2dKswjx/XQ476nGEe9aal27oHEgT2oc19lybijX71wEi8qb8\\n0aKFqaxkBjabB2yQvNKm9kd8SQP0Y+xDfKH2A0uIwLnBHV+F8Pq0cblHn0nUi0V2\\nOMVpBVkCgYA3X9aOpEKDK6IuNhqWsXb6mkEvHV/zvO6XBYCp2VAtkpSjoiWEM6Wt\\nxcGyWLeQ+NWaOLx+wWHXkpxxN7k8Z+WYAi7GsuBdsvwKxK+YouMdjclGseNcYcBZ\\ngJRfqLCIyshxOUfbpvnA3zeL2v4B7AQKZ0nIS2tUmJQESYajQ7/9sQKBgQCs5fPM\\n4Wgb17rUQ0RTjMFAt/BOpH73qbfql6J41AvpOVddM7yB2SNVsKFgZh8hl/qrkmWX\\nMhhMR8+W61V9h1KFln/LjolbA8WmbUWSIWUMzcUzSy75c28hivM7E4DvprXDe5sP\\ntU9OKO1AlRw5Nty1ciXLZZN5Zc+2L4HISrEfWQKBgQCxfzYdt1NewpSCMOWXZLTo\\nNS3xq4XcAMIZm+NkrhGUJxlrH80iik3PCJmg3gieFRWoOCVj6/3ftNGgowzOOtl5\\nuluwonp3rfeyNQwYo4uwCl89UgTtD1hjG8JOdi4kfDJmzPCrhX8PULOe2q6pPUhh\\nsPKnuTdzDZdZujDfDKtVLQ==\\n-----END PRIVATE KEY-----\\n\", \"client_email\": \"firebase-adminsdk-fbsvc@grad-51668.iam.gserviceaccount.com\", \"client_id\": \"104563635688946380444\", \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\", \"token_uri\": \"https://oauth2.googleapis.com/token\", \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\", \"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40grad-51668.iam.gserviceaccount.com\", \"universe_domain\": \"googleapis.com\"}"

        # Parse the JSON string to a dictionary
        try:
            firebase_key_dict = json.loads(firebase_key_str)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Firebase key. Check its format: {e}")
            st.stop()
        cred = credentials.Certificate(firebase_key_dict)
        firebase_admin.initialize_app(cred)
    
    return {
        'auth': auth,
        'db': firestore.client()
    }

firebase = initialize_firebase()
