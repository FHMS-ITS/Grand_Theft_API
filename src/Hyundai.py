import requests
import BlueLinkyStamps as bls
from Vehicle import Vehicle
from VehConst import VehConst

## Constant URL for all other api calls
HOST_URL = "https://prd.eu-ccapi.hyundai.com:8080"
## Constant URL for generating an access token (using refresh token)
TOKEN_URL = HOST_URL+"/api/v1/user/oauth2/token"

## Hyundai Class
# implements all Hyundai API calls
# extends Vehicle Class
class Hyundai(Vehicle):

    ## Hyundai Constructur
    # Read the Hyundai-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variabls of Audi class
    def __init__(self,verbose):
        super().__init__(VehConst.HYUNDAI_TF_PATH,verbose)
        ## Manufacture name as String in lowercase "hyundai"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.expires_in = ""
        self.token_type = ""
        self.argv = ("access_token","refresh_token","authorization","expires_in","token_type")
        self.setattr_from_csv(*self.argv)
        ## authorization seems to be constant, and was extracted using mitmproxy
        self.authorization = "NmQ0NzdjMzgtM2NhNC00Y2YzLTk1NTctMmExOTI5YTk0NjU0OktVeTQ5WHhQekxwTHVvSzB4aEJDNzdXNlZYaG10UVI5aVFobUlGampvWTRJcHhzVg=="
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------

    ## API request to get the vehicle(s) linked to the user's account
    # gives basic information about the vehicle(s)
    def get_vehicles(self):
        self.logger.url = HOST_URL+"/api/v1/spa/vehicles"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## API request to get user profile( data
    # gives basic information about the user profile
    def get_user_profile(self):
        self.logger.url = HOST_URL+"/api/v1/user/profile"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()


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
        self.logger.response  = requests.post(self.logger.url, headers=self.logger.header, data=self.logger.body)
        if self.verbose:
            self.logger.log_req_res()
        self.setattr_from_res(self.logger.response,*self.argv)

    def cred_auth(self, username, password):
        print("not yet implemented")

#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## returns the requested HTTP Headers Dictionary of bmw requests
    # example get_headers("TOKEN_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
            "TOKEN_HEADERS": { 
                "Authorization": "Basic "+self.authorization,
                "Connection": "close",
                "ccsp-service-id":"6d477c38-3ca4-4cf3-9557-2a1929a94654",
                "offset":"1",
                "ccsp-device-id":"35f8dbce-bf1c-4863-afce-c6908df49ed8",
                "ccsp-application-id":"014d2225-8495-4735-812d-2616334fd15d",
                "Stamp": bls.get_bluelinky_stamp(self.verbose),
                "ccuCCS2ProtocolSupport":"0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host":"prd.eu-ccapi.hyundai.com",
                "Accept-Encoding":"gzip",
                "User-Agent":"okhttp/3.12.12"
            },
            "REQ_HEADERS": {
                "Connection": "close",
                "ccsp-service-id": "6d477c38-3ca4-4cf3-9557-2a1929a94654",
                "offset": "1",
                "Authorization":"Bearer "+self.access_token,
                "ccsp-device-id": "35f8dbce-bf1c-4863-afce-c6908df49ed8",
                "ccsp-application-id": "014d2225-8495-4735-812d-2616334fd15d",
                "Stamp": bls.get_bluelinky_stamp(self.verbose),
                "Host": "prd.eu-ccapi.hyundai.com",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/3.12.12"
            }
        }
        return headers[header]
    
    ## internal helper: used to build body for refresh_tokens
    def __get_token_data(self):
        data = "client_id=6d477c38-3ca4-4cf3-9557-2a1929a94654"
        data +="&grant_type=refresh_token"
        data +="&refresh_token=" + self.refresh_token
        data +="&redirect_uri=https://prd.eu-ccapi.hyundai.com:8080/api/v1/user/oauth2/redirect"
        return data