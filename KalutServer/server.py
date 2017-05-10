from KalutServer.Model.Communicator import Communicator
from KalutServer.RESTfulAPI.server import start_server
from KalutServer.Exceptions import *
import threading

### ENTRY POINT ###
def RunKalutServer():
    # RESTful API
    print 'Initializing RESTful API...'
    RESTfulAPI_thread = threading.Thread(target=RESTfulAPI_main, name='RESTfulAPI_thread', )
    RESTfulAPI_thread.daemon = True
    RESTfulAPI_thread.start()

    # Connection to the Database
    
    
    RESTfulAPI_thread.join()

def RESTfulAPI_main():
    start_server()

if __name__=='__main__':
    pass