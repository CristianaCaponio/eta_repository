from mongoengine import connect

client = connect(
    db='followtruck',
    username='root',
    password='1234',
    host='mongodb://root:1234@localhost/followtruck'
)

def db_connect():
    #connecting to a DB in mongoDB
    try:
        if client.get_database('followtruck'):
            print("Connection Successful!")
            return True
    except:
        print("Please check your connection")
        return False
    
   