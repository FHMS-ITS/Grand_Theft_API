import requests
from Vehicle import Vehicle
from VehConst import VehConst

## Constant URL for generating an access token (using refresh token)
TOKEN_URL = "https://mbboauth-1d.prd.ece.vwg-connect.com/mbbcoauth/mobile/oauth2/v1/token"
## Constant URL for all other api calls
HOST_URL = "https://fal-3a.prd.eu.dp.vwg-connect.com/fs-car/vehicleMgmt/vehicledata/v2/Audi/DE"

## Audi Class
# implements Audi API calls
# extends Vehicle Class
class Audi(Vehicle):
    
    ## Audi Constructur
    # Read the Audi-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variabls of Audi class
    def __init__(self,verbose):
        super().__init__(VehConst.AUDI_TF_PATH,verbose)
        ## Manufacture name as String in lowercase "audi"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.expires_in = ""
        self.refresh_expires_in = ""
        self.argv = ("access_token","refresh_token","expires_in","refresh_expires_in")
        self.setattr_from_csv(*self.argv)
        self.vin = ""
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------
    
    ## API request to get the vehicle(s) linked to the user's account
    # gives basic information about the vehicle(s)
    def get_vehicles(self):
        self.logger.url =  HOST_URL+"/vehicles/"+self.vin
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()
    ##
    #TODO: implement get vin
    def __get_vin(self):
        return


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
    # example get_headers("TOKEN_HEADERS"), get_headers("AUTH_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, AUTH_HEADERS_3, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
             "TOKEN_HEADERS": { 
                "Accept": "application/json",
                "Accept-Charset": "utf-8",
                "X-Client-ID": "becdd944-a10a-4d79-9aed-c6acb754f06e",
                "User-Agent": "myAudi-Android/4.12.0 (Build 800238096.2208171253) Android/9",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "mbboauth-1d.prd.ece.vwg-connect.com",
                "Connection": "Keep-Alive" 
            },
            "REQ_HEADERS": {
                "H.AUTH_TOKEN ": "Bearer "+self.access_token,
                "x-user-agent": "ioBroker v50"
            }
        }
        return headers[header]
    
    ## internal helper: used to build json body for refresh_tokens
    def __get_token_data(self):
        data = {
            "grant_type": "refresh_token",
            "token": self.refresh_token,
            "scope": "sc2:fal",
            "vin": self.vin
        }
        return data
    