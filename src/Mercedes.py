import requests
import json
from Vehicle import Vehicle
from VehConst import VehConst

## Constant URLs for data api calls
HOST_URL = "https://bff.emea-prod.mobilesdk.mercedes-benz.com"
## found in ioBroker source code
HOST_URL_IO = "https://bff-prod.risingstars.daimler.com"
HOST_URL_2 = "https://api.mercedes-benz.com"
## Constant URL for authentification with credentials
AUTH_URL = HOST_URL+"/v1/login"
## Constant URL for generating an access token (using refresh token)
TOKEN_URL = "https://id.mercedes-benz.com/as/token.oauth2"

## Mercedes Class
# implements Mercedes API calls
# extends Vehicle Class
class Mercedes(Vehicle):
    
    ## Mercedes Constructur
    # Read the Mercedes-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variabls of Mercedes class
    def __init__(self,verbose):
        super().__init__(VehConst.MERCEDES_TF_PATH,verbose)
        ## Manufacture name as String in lowercase "mercedes"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.expires_in = ""
        self.token_type = ""
        self.argv = ("access_token","refresh_token","expires_in","token_type")
        self.setattr_from_csv(*self.argv)
        self.vin = ""
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------
  
    ## API request to get the vehicle(s) linked to the user's account
    # gives basic information about the vehicle(s), source is ioBroker: https://github.com/TA2k/ioBroker.mercedesme/blob/master/main.js
    def get_vehicles_iobroker(self):
        self.logger.url =  HOST_URL_IO+"/v2/vehicles?locale=de"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## API request to get the vehicle(s) linked to the user's account
    # gives basic information about the vehicle(s), source is reversing of MercedesMe Android App
    def get_vehicles_app(self):
        self.logger.url =  HOST_URL+"/v2/vehicles"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## API request to get a vehicle's consumption
    def get_consumption(self):
        self.logger.url =  HOST_URL+"/v1/vehicle/" + self.vin + "/consumption"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## API request to get a vehicle's capabilities. 
    # example: consumption, or possibly lock status
    def get_capabilities(self):
        self.logger.url =  HOST_URL+"/v1/vehicle/" + self.vin + "/capabilities"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## internal helper: sends a request equivalent to get_vehicles_app and updates self.vin accordingly
    def __get_vin(self):
        data_url = HOST_URL+"/v2/vehicles"
        response = requests.post(data_url, headers=self.get_headers("REQ_HEADERS"))
        if response.status_code != 200 and response.status_code != 207:
            self.vprint("mercedes: to get vin access token must be valid")
            return
        res_body = response.json()
        result = json.loads(json.dumps(res_body))
        try:
            self.vin = result["assignedVehicles"][0]["fin"]
            self.vprint(self.__class__.__name__ + " VIN: " + self.vin)
        except IndexError:
            self.vprint(self.__class__.__name__ + " VIN not found")
        


#----------------------------------- AUTH REQUESTS #-----------------------------------

    ## set the member variable refresh_token
    # and then calls the function refresh_tokens to acquire new tokens
    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token
        self.refresh_tokens()

    ## set the member variable access_token
    # and then calls the function update_csv to update he csv-file
    def set_access_token(self, access_token):
        self.access_token = access_token
        self.update_csv(*self.argv)
        self.__get_vin()

    ## Function for generating access token using refresh token
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response
    # and call setattr_from_res(self.logger.response,*self.argv) *self.argv is set in constructor 
    # setattr_from_res sets the member variables of the class by reading new values from the response 
    # setattr_from_res also updates the csv file by calling update_csv internally
    def refresh_tokens(self):
        self.logger.url = TOKEN_URL
        self.logger.header = self.get_headers("TOKEN_HEADERS")
        self.logger.body = self.__get_token_data()
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, json=self.logger.body)
        if self.verbose:
            self.logger.log_req_res()
        self.setattr_from_res(self.logger.response,*self.argv)
        self.__get_vin() 

    ## Function to get the Mercedes PIN (one time password)
    # user has to enter email / phone number first and then type in the PIN
    # is called before cred_auth in ReqCreator
    def get_pin(self, username):
        self.logger.url = AUTH_URL
        self.logger.header = self.get_headers("AUTH_HEADERS")
        self.logger.body = {
            "countryCode":"US",
            "emailOrPhoneNumber":username,
            "nonce":"7c5e7e18-0970-409f-8b76-ee9f1dbe4a87"
        }
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, json=self.logger.body)
        self.logger.log_req_res()

    ## Function to initiate login using credentials (which includes PIN for Mercedes)
    # is called after get_pin in ReqCreator, because PIN has to received first
    def cred_auth(self, username, pin):
        self.logger.url = TOKEN_URL
        self.logger.header = self.get_headers("TOKEN_PIN_HEADERS")
        data = "client_id=01398c1c-dc45-4b42-882b-9f5ba9f175f1"
        data += "&grant_type=password"
        data += "&password=7c5e7e18-0970-409f-8b76-ee9f1dbe4a87:"+pin
        data += "&scope=openid email phone profile offline_access ciam-uid"
        data += "&username="+username
        self.logger.body = data
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, data=self.logger.body) 
        self.setattr_from_res(self.logger.response,*self.argv)
        self.__get_vin()

#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## returns the requested HTTP Headers Dictionary of bmw requests
    # example get_headers("TOKEN_HEADERS"), get_headers("AUTH_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, REQ_HEADERS, TOKEN_PIN_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
             "TOKEN_HEADERS": { 
                "Stage": "prod",
                "X-ApplicationName": "mycar-store-ece",
                "ris-application-version": "1.25.0",
                "ris-os-name": "android",
                "ris-os-version": "9",
                "ris-sdk-version": "2.79.0",
                "User-Agent": "mycar-store-ece v1.25.0, android 9, SDK 2.79.0",
                "X-Locale": "en-US",
                "X-SessionId": "fa33ef9d-6395-4811-89a0-579c636328e7",
                "X-TrackingId": "7e940b4a-9089-47f0-a198-1d9cac02d036",
                "X-Device-Id": "e583dbd5-ce81-4e3a-a0e4-7fe7bc44a675",
                "X-Request-Id": "7e940b4a-9089-47f0-a198-1d9cac02d036",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "id.mercedes-benz.com",
                "Connection": "Keep-Alive"
            },
            "AUTH_HEADERS": { 
                "X-ApplicationName": "mycar-store-ece",
                "ris-application-version": "1.28.0",
                "ris-os-name": "android",
                "ris-os-version": "13",
                "ris-sdk-version": "2.86.2",
                "User-Agent": "mycar-store-ece v1.28.0, android 13, SDK 2.86.2",
                "X-Locale": "en-US",
                "X-SessionId": "a9dfff351-29b0-446c-845c-4aff94e22680",
                "X-TrackingId": "77b684ff-ca07-435d-a329-da6e964451bf",
                "Content-Type": "application/json; charset=UTF-8",
                "Connection": "Keep-Alive"
            },
            "TOKEN_PIN_HEADERS": {
                "Stage": "prod",
                "device-uuid": "6e656bc9-c163-432e-8c6a-a1700322d0c5",
                "X-ApplicationName": "mycar-store-ece",
                "ris-application-version": "1.28.0",
                "ris-os-name": "android",
                "ris-os-version": "13",
                "ris-sdk-version": "2.86.2",
                "User-Agent": "mycar-store-ece v1.28.0, android 13, SDK 2.86.2",
                "X-Locale": "en-US",
                "X-SessionId": "9dfff351-29b0-446c-845c-4aff94e22680",
                "X-TrackingId": "45a5e9fb-0fb2-4abf-bedc-7c01eccf7ac3",
                "X-Device-Id": "6e656bc9-c163-432e-8c6a-a1700322d0c5",
                "X-Request-Id": "45a5e9fb-0fb2-4abf-bedc-7c01eccf7ac3",
                "Content-Type": "application/x-www-form-urlencoded",
                "Connection": "Keep-Alive"
            },
            "REQ_HEADERS": {
                "Authorization" : "Bearer "+self.access_token, 
                "User-Agent" : "mycar-store-ece v1.28.0, android 13, SDK 2.86.2",
                "X-SessionId" : "6879ed61-ff53-4c12-b9fb-a10bdf03ee1a", 
                "X-TrackingId" : "8c198dab-b6c1-4d72-be73-88b6b353aee9", 
                "X-Locale" : "de-CH", 
                "ris-os-name" : "android", 
                "ris-sdk-version": "2.86.2"
            }
        }
        return headers[header]
    
    ## internal helper: used to build json body for refresh_tokens
    def __get_token_data(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        return data
    