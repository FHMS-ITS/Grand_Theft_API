import requests
from Vehicle import Vehicle
from VehConst import VehConst

## Constant URL for generating an access token (using refresh token)
TOKEN_URL = "https://template-token.com"
## Constant URL for authentification with credentials
AUTH_URL = "https://template-oauth.com"
## Constant URL for all other api calls
HOST_URL = "https://template-host.com"

## Template Class
# implements all Template api calls
# extends Vehicle Class
class Template(Vehicle):
    
    ## Template Constructur
    # Read the Template-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variables of Template class
    def __init__(self,verbose):
        super().__init__(VehConst.TEMPLATE_TF_PATH,verbose)
        # or self.mf_tf_path = self.__class__.__name__.upper() + "_TF_PATH"
        # super().__init__(getattr(VehConst, self.mf_tf_path), verbose)
        ## Manufacturer name as String in lowercase "template"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        ## access_token, refresh_token, template_token1 ... are the refresh_tokens and cred_auth response's attributes 
        self.argv = ("access_token","refresh_token","template_token1","template_token2")
        self.setattr_from_csv(*self.argv)
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------
    
    ## Template for get ressource
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response 
    def get_ressource_template(self):
        self.logger.url = HOST_URL +"/ressource"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.body = "data_template"
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header, data=self.logger.body)
        self.logger.log_req_res()

    ## ... more api requests


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
        # if only access_token has to be updated
        # self.update_csv("access_token")

    ## Template for generating access token using refresh token
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response
    # and call setattr_from_res(self.logger.response,*self.argv) *self.argv is set in constructor 
    # setattr_from_res sets the member variables of the class by reading new values from the response 
    # setattr_from_res also updates the csv file by calling update_csv internally
    def refresh_tokens(self):
        self.logger.url = TOKEN_URL
        self.logger.header = self.get_headers("TOKEN_HEADERS")
        self.logger.body = "data for refreshing tokens"
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, data=self.logger.body)
        self.logger.log_req_res()
        self.setattr_from_res(self.logger.response,*self.argv)
        
    ## Template for generating access token, refresh token from credentials
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response
    # and call setattr_from_res(self.logger.response,*self.argv) *self.argv is set in constructor 
    # setattr_from_res sets the member variables of the class by reading new values from the response
    # setattr_from_res also updates the csv file by calling update_csv internally
    # @param username email
    # @param password password
    def cred_auth(self, username, password):
        self.logger.url = AUTH_URL
        self.logger.header = self.get_headers("AUTH_HEADERS")
        self.logger.body = {
            "username":username,
            "password":password,
            "template":"value"
        }
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, json=self.logger.body)
        self.logger.log_req_res()
        self.setattr_from_res(self.logger.response,*self.argv)


#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## internal helper: returns the requested HTTP Headers Dictionary
    # example get_headers("TOKEN_HEADERS"), get_headers("AUTH_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
             "TOKEN_HEADERS": { 
                "x-dynatrace": "template",
                "Content-Type": "application",
                "Connection": "Keep-Alive"
                },
            "AUTH_HEADERS": { 
                "Content-Type": "application",
                "Accept": "application/json, text/plain, */*"
                },
            "REQ_HEADERS": {
                    "Authorization" : "Bearer "+self.access_token,
                    "Accept-charset" : "UTF-8",
                    "x-user-agent" : "template"
            }
        }
        return headers[header]