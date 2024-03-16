from Renault import Renault

## apikey is subject to change, check here for latest apikey: https://raw.githubusercontent.com/hacf-fr/renault-api/main/src/renault_api/const.py
## updatekey is subject to change, check here for latest Kamereon API key: https://raw.githubusercontent.com/db-EV/ZoePHP/main/src/api-keys.php
## if the request start to fail, try replacing the keys in superclass Renault.py

## Dacia Class
# shares properties with superclass Renault
# extends Renault Class
class Dacia(Renault):
    
    ## Dacia Constructor
    # call constructor of superclass Renault and pass verbose
    def __init__(self, verbose):
        super().__init__(verbose)
