import requests
import json
from datetime import datetime
from Vehicle import Vehicle
from VehConst import VehConst

## Constant URL for retrieving customer account meta data
CUSTOMER_URL = "https://apis.renault.com/myr/api/v1/connection?&country=DE&product=MYRENAULT&locale=de-DE&displayAccounts=MYRENAULT"
## Constant URL for generating an access token (according to Renault JWT)
TOKEN_URL = "https://accounts.eu1.gigya.com/accounts.getJWT"
## Constant URL for authentification with credentials
AUTH_URL = "https://accounts.eu1.gigya.com/accounts.login"
## Constant base URL for all other api calls
HOST_URL = "https://api-wired-prod-1-euw1.wrd-aws.com/commerce/v1/accounts/"

## Renault Class
# implements available Renault api calls
# extends Vehicle Class
class Renault(Vehicle):
    
    ## Renault Constructor
    # Read the subclass-csv-file content such as access token, refresh token and metadata
    # then assign their values to the member variables of Renault class
    def __init__(self, verbose):
        self.mf_tf_path = self.__class__.__name__.upper() + "_TF_PATH"
        super().__init__(getattr(VehConst, self.mf_tf_path), verbose)
        ## Manufacture name as String in lowercase "renault" or "dacia"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.id_token = ""
        self.login_token = ""
        # if the requests start to fail, try update the apikey/updatekey below
        self.argv = ("login_token", "id_token", "apikey","updatekey")
        self.setattr_from_csv(*self.argv)
        self.accountId = ""
        self.vin = ""
        ## apikey is subject to change, check here for latest "gigya_apikey" (in our case DE): https://raw.githubusercontent.com/hacf-fr/renault-api/main/src/renault_api/const.py
        ## updatekey is subject to change, check provided url for latest "Kamereon API" key. Alternatively try: https://raw.githubusercontent.com/db-EV/ZoePHP/main/src/api-keys.php
        self.apikey = "3_7PLksOyBRkHv126x5WhHb-5pqC1qFR8pQjxSeLB6nhAnPERTUlwnYoznHSxwX668"
        self.updatekey = "YjkKtHmGfaceeuExUDKGxrLZGGvtVS0J"
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------
             
    ## API request to get general data on the user and the account
    def get_user_data(self):
        self.logger.response = requests.post(CUSTOMER_URL, headers=self.get_headers("REQ_HEADERS"))
        self.logger.url = CUSTOMER_URL
        self.logger.method = "POST"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.log_req_res()

    ## API request to get the vehicle(s) linked to the user's account
    def get_vehicles(self):
        if self.accountId is not None:
            data_url = HOST_URL + self.accountId + "/vehicles?country=de&oms=false"
            self.logger.response = requests.get(data_url, headers=self.get_headers("REQ_HEADERS"))
            self.logger.url = data_url
            self.logger.header = self.get_headers("REQ_HEADERS")
            self.logger.log_req_res()

    ## API request to get the vehicle's battery status
    def get_battery_status(self):
        if self.__get_arbitrary_ressource("battery-status", "v2"):
            self.logger.log_req_res()

    ## API request to get the vehicle's battery inhibition status
    def get_battery_inhibition_status(self):
        if self.__get_arbitrary_ressource("battery-inhibition-status", "v1"):
            self.logger.log_req_res()
    
    # API request for cockpit exsists with v1 and v2, both outputs were equal with the tested Dacia (basic data like mileage)
    def get_cockpit(self, version):
        if self.__get_arbitrary_ressource("cockpit", version):
            self.logger.log_req_res()

    ## API request to get the vehicle's charge mode
    def get_charge_mode(self):
        if self.__get_arbitrary_ressource("charge-mode", "v1"):
            self.logger.log_req_res()

    ## API request to get the vehicle's hvac status (heating, ventilation, air conditioning)
    def get_hvac_status(self):
        if self.__get_arbitrary_ressource("hvac-status", "v1"):
            self.logger.log_req_res()

    ## API request to get the vehicle's hvac settings (heating, ventilation, air conditioning)
    def get_hvac_settings(self):
        if self.__get_arbitrary_ressource("hvac-settings", "v1"):
            self.logger.log_req_res()

    ## API request to get the vehicle's charging settings
    def get_charging_settings(self):
        if self.__get_arbitrary_ressource("charging-settings", "v1"):
            self.logger.log_req_res()
       
    ## API request to get the vehicle's charge history 
    def get_charge_history(self):
        if self.__check_accountId_and_vin():
            date_str = datetime.now().strftime('%Y-%m-%d')
            data_url = HOST_URL + self.accountId + "/kamereon/kca/car-adapter/v1/cars/"
            data_url += self.vin + "/charge-history?type=day&start=1970-01-01&end="
            data_url += date_str + "&country=de"
            self.logger.response = requests.get(data_url, headers=self.get_headers("REQ_HEADERS"))
            self.logger.url = data_url
            self.logger.header = self.get_headers("REQ_HEADERS")
            self.logger.log_req_res()

    ## API request to get the vehicle's charges     
    def get_charges(self):
        if self.__check_accountId_and_vin():
            date_str = datetime.now().strftime('%Y-%m-%d')
            data_url = HOST_URL + self.accountId + "/kamereon/kca/car-adapter/v1/cars/"
            data_url += self.vin + "/charges?start=1970-01-01&end="
            data_url += date_str + "&country=de"
            self.logger.response = requests.get(data_url, headers=self.get_headers("REQ_HEADERS"))
            self.logger.url = data_url
            self.logger.header = self.get_headers("REQ_HEADERS")
            self.logger.log_req_res()

    ## API request to get information on the vehicle's lock state
    def get_lock_status(self):
        if self.__get_arbitrary_ressource("lock-status", "v1"):
            self.logger.log_req_res()

    ## API request to get information on the vehicle's res state
    def get_res_state(self):
        if self.__get_arbitrary_ressource("res-state", "v1"):
            self.logger.log_req_res()

    ## API request to get the vehicle's position (lat/long) and heading (direction)
    def get_location(self):
        if self.__get_arbitrary_ressource("location", "v1"):
            self.logger.log_req_res()


#----------------------------------- AUTH REQUESTS #-----------------------------------
    
    ## sets a new login_token and updates the according member variables
    def set_refresh_token(self, refresh_token):
        self.login_token = refresh_token
        self.refresh_tokens()

    ## sets a new id_token and updates the according member variables
    def set_access_token(self, access_token):
        self.id_token = access_token
        self.__update_tokens()

    ## generate new access token and update the member variables and csv-file
    def refresh_tokens(self):
        response = requests.post(TOKEN_URL, headers=self.get_headers("TOKEN_HEADERS"), data=self.__get_token_data())
        self.logger.url = TOKEN_URL
        self.logger.body = self.__get_token_data()
        self.logger.header = self.get_headers("TOKEN_HEADERS")
        self.logger.response = response
        if self.verbose:
            self.logger.log_req_res()
        return self.__update_id_token(response)

    ## generate new access token, refresh token from credential and update the member variables and csv-file
    # @param username email
    # @param password password
    # @see ~/docs/drafts/renault auth.png
    def cred_auth(self, username, password):
        data = self.__get_auth_data()
        data+= "&loginID=" + username
        data+= "&password=" + password
        session = requests.Session()
        response = requests.post(AUTH_URL, headers=self.get_headers("AUTH_HEADERS"), data=data)
        self.logger.url = AUTH_URL
        self.logger.body = data
        self.logger.header = self.get_headers("AUTH_HEADERS")
        self.logger.response = response
        self.logger.log_req_res()
        if response.status_code == 200:
            res_body = response.json()
            result = json.loads(json.dumps(res_body))
        self.__update_login_token(response)
            
        return self.login_token
            

#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## returns the requested HTTP Headers Dictionary of renault requests
    # example get_headers("TOKEN_HEADERS"), get_headers("AUTH_HEADERS"), get_headers("REQ_HEADERS")
    # @param header Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
             "TOKEN_HEADERS": { 
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "MYRenault/39 CFNetwork/1312 Darwin/21.0.0",
                "Cache-Control": "no-cache",
                "Connection": "Keep-Alive"
                },
            "AUTH_HEADERS":  {
                "User-Agent": "MYRenault/39 CFNetwork/1312 Darwin/21.0.0",
                "Accept": "*/*",
                "Accept-Language": "de-de",
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded"
},
            "REQ_HEADERS": {
                    "x-gigya-id_token" : self.id_token,
                    "apikey": self.updatekey,
                    "Content-Type" : "application/json",
                    "User-Agent" : "MYRenault/39 CFNetwork/1312 Darwin/21.0.0"
            }
        }
        return headers[header]
    
    ## returns the x-www-form-urlencoded body for the refresh_token request
    # requires valid login_token (similar usage to refresh_token) and apikey
    def __get_token_data(self):
        data = "format=json&login_token=" + self.login_token
        data += "&sdk=js_latest&fields=data.personId%2Cdata.gigyaDataCenter"
        data += "&apikey=" + self.apikey
        # expiration is the equivalent of 10 years in seconds (maximum value)
        data += "&expiration=315360000" 
        return data
    
    ## returns the x-www-form-urlencoded body for the initial auth request
    # requires valid apikey   
    def __get_auth_data(self):
        data = "apikey=" + self.apikey
        data += "&format=json&httpStatusCodes=false"
        data += "&sdk=js_latest&include=profile%2Cdata"
        return data
    
    ## internal helper: extracts the id_token from a response, updates member variables and returns the new id_token
    def __update_id_token(self, response: requests.Response):
        self.vprint("Status Code", response.status_code)
        self.vprint("JSON Response ", response.json())
        if response.status_code == 200:
            data = response.json()
            result = json.loads(json.dumps(data))
            self.vprint(result)
            try:
                self.id_token = result["id_token"]
            except:
                self.id_token = ""
                print(f"{self.__class__.__name__}: id_token not found")
        self.__update_tokens()
        return self.id_token

    ## internal helper: extracts the login_token from a response, updates member variables and returns the new login_token
    def __update_login_token(self, response: requests.Response):
        self.vprint("Status Code", response.status_code)
        self.vprint("JSON Response ", response.json())
        if response.status_code == 200:
            data = response.json()
            result = json.loads(json.dumps(data))
            self.vprint(result)
            try:
                self.login_token = result["sessionInfo"]["cookieValue"]
            except:
                self.login_token = ""
                print(f"{self.__class__.__name__}: login_token not found")
        self.__update_tokens()
        return self.login_token
    
    ## internal helper: updates the currents member variables (id_token, login_token ..) to the csv-file
    def __update_tokens(self):
        self.update_csv(*self.argv)
        self.accountId = self.__get_account_id()
        self.vin = self.__get_vin()

    ## internal helper: call get_vehicles and return the first linked VIN if it exists
    # requires valid id_token and accountId
    # @return VIN on success, None on error
    def __get_vin(self):
        try:
            response = requests.get(HOST_URL + self.accountId + "/vehicles?country=de&oms=false", headers=self.get_headers("REQ_HEADERS"))
        except:
            print(f'Could not get {self.__class__.__name__} VIN')
            return None
        if response.status_code != 200 and response.status_code != 207:
            print("access token must be valid")
            return None
        if self.accountId is not None:
            res_body = response.json()
            result = json.loads(json.dumps(res_body))
            try:
                self.vprint(self.__class__.__name__ + " VIN: " + result["vehicleLinks"][0]["vin"])
                return result["vehicleLinks"][0]["vin"]
            except IndexError:
                self.vprint(self.__class__.__name__ + " VIN not found")
        else:
            return None

    ## internal helper: get the renault/dacia accountId
    # @return accountId on success, None on error
    def __get_account_id(self):
        ## returns either "MYRENAULT" or "MYDACIA"
        account_type = "MY" + self.__class__.__name__.upper()
        self.vprint("ACCOUNT_TYPE: " + account_type)
        response = requests.post(CUSTOMER_URL, headers=self.get_headers("REQ_HEADERS"))
        if response.status_code != 200 and response.status_code != 207:
            print(f"failed to retrieve {self.__class__.__name__} accountId")
            return None
        res_body = response.json()
        result = json.loads(json.dumps(res_body))
        
        for account in result["currentUser"]["accounts"]:
            if account["accountType"] == account_type:
                self.vprint("account: " + account["accountId"])
                return(account["accountId"])
        
        print("error retrieving accountId")
        return None

    ## internal helper: call kamereon API (renault/dacia) with dynamic ressource and version if accountId and vin are valid
    # example: https://api-wired-prod-1-euw1.wrd-aws.com/commerce/v1/accounts/{accountId}/kamereon/kca/car-adapter/v1/cars/{VIN}/location?country=de
    # @param ressource ressource as string, examples: "location", "battery-status"
    # @param version version as string, usually "v1" or "v2"
    # @return boolean value if request was sent successfully or not
    def __get_arbitrary_ressource(self, ressource: str, version: str):
        constantsValid = self.__check_accountId_and_vin()
        if constantsValid:
            data_url = HOST_URL
            data_url += self.accountId
            data_url += "/kamereon/kca/car-adapter/" + version + "/cars/"
            data_url += self.vin
            data_url += "/" + ressource + "?country=de"
            self.logger.response = requests.get(data_url, headers=self.get_headers("REQ_HEADERS"))
            # self.logger...
            return True
        else:
            return constantsValid

    ## internal helper: returns whether accountId and VIN are valid or not
    # @return boolean value, True if accountId and VIN valid, else False
    def __check_accountId_and_vin(self):
        if self.accountId is not None and self.vin is not None:
            return True
        else:
            print("This API Call requires a valid accountId and VIN, you should try and regenerate tokens")
            return False            