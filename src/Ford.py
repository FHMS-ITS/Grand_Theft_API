import requests
import json
from Vehicle import Vehicle
from VehConst import VehConst

##Constant URL HOST for some API calls
CUSTOMER_URL = "https://api.mps.ford.com"
## Constant URL for generating an access token (using refresh token)
TOKEN_URL = CUSTOMER_URL + "/api/token/v2/cat-with-refresh-token"
## Constant URL for all other API calls
HOST_URL = "https://usapi.cv.ford.com"

## Ford Class
# implements Ford API calls
# extends Vehicle Class
class Ford(Vehicle):
    
    ## Ford Constructur
    # Read the Ford-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variabls of Ford class
    def __init__(self,verbose):
        super().__init__(VehConst.FORD_TF_PATH,verbose)
        ## Manufacture name as String in lowercase "ford"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.ford_consumer_id = ""
        self.expires_in = ""
        self.refresh_expires_in = ""
        self.argv = ("access_token","refresh_token","ford_consumer_id","expires_in","refresh_expires_in")
        self.setattr_from_csv(*self.argv)
        self.vin = ""
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------

    ## API request to get general data on the user and the account
    def get_user_data(self):
        self.logger.url = CUSTOMER_URL + "/api/users?lrdt=5-15-2015"
        self.logger.header = self.get_headers("USERDATA_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## API request to get the vehicle(s) linked to the user's account
    # gives basic information about the vehicle status
    def get_vehicles_status(self):
        self.logger.url = HOST_URL + "/api/vehicles/v4/" + self.vin + "/status"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

     ## API request to get the expdashboard details
    def get_expdashboard_details(self):
        self.logger.url = CUSTOMER_URL + "/api/expdashboard/v1/details/"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.body = { "dashboardRefreshRequest": "all" }
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, json=self.logger.body)
        self.logger.log_req_res()

    ## internal helper: make call equivalent to get_expdashboard_details and return the first linked VIN if it exists
    # requires valid access_token
    def __get_vin(self):
        data_url = CUSTOMER_URL + "/api/expdashboard/v1/details/"
        data = { "dashboardRefreshRequest": "all" }
        response = requests.post(data_url, headers=self.get_headers("REQ_HEADERS"), json=data)
        if response.status_code != 200 and response.status_code != 207:
            self.vprint("ford: to get vin access token must be valid")
            return
        res_body = response.json()
        result = json.loads(json.dumps(res_body))
        try:
            self.vin = result["userVehicles"]["vehicleDetails"][0]["VIN"]
            self.vprint(self.__class__.__name__ + " VIN: " + self.vin)
        except IndexError:
            self.vprint(self.__class__.__name__ + " VIN not found")
        
    
#----------------------------------- AUTH REQUESTS #-----------------------------------

    ## set the member variable refresh_token
    # then calls the function refresh_tokens to acquire new tokens
    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token
        self.refresh_tokens()

    ## set the member variable access_token
    # and then calls the function update_csv to update the csv-file
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

    def cred_auth(self, username, password):
        print("not yet implemented")
        self.__get_vin()


#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## returns the requested HTTP Headers Dictionary of bmw requests
    # example get_headers("TOKEN_HEADERS"), get_headers("USERDATA_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
            "TOKEN_HEADERS": { 
            "x-dynatrace": "MT_3_26_1799289111_16-0_997d5837-2d14-4fbb-a338-5c70d678d40e_1_518_22",
            "application-id": "667D773E-1BDC-4139-8AD0-2B16474E8DC7",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "okhttp/4.9.2"
            },
            "REQ_HEADERS": {
                "auth-token" : self.access_token,
                "application-id" : "667D773E-1BDC-4139-8AD0-2B16474E8DC7",
                "countrycode": "DEU",
                "locale": "de-DE",
                "content-type": "application/json; charset=UTF-8",
                "user-agent" : "okhttp/4.9.2"
            },
            "USERDATA_HEADERS": {
                "auth-token" : self.access_token,
                "application-id" : "667D773E-1BDC-4139-8AD0-2B16474E8DC7",
                "x-dynatrace": "MT_3_26_1799289111_16-0_997d5837-2d14-4fbb-a338-5c70d678d40e_1_518_22",
                "user-agent" : "okhttp/4.9.2"
            }
        }
        return headers[header]
    
    ## internal helper: used to build json body for refresh_tokens
    def __get_token_data(self):
        data = {
            "refresh_token": self.refresh_token
        }
        return data
    