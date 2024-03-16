import requests
import json
import urllib.parse
import time
import sys
from datetime import date
from datetime import datetime
from Vehicle import Vehicle
from VehConst import VehConst

##Constant URL for getting account meta data
CUSTOMER_URL = "https://customer.bmwgroup.com/gcdm"
## Constant URL for generating an access token (using refresh token)
TOKEN_URL = CUSTOMER_URL+"/oauth/token"
## Constant URL for authentification with credentials
AUTH_URL = CUSTOMER_URL+"/oauth/authenticate"
## Constant URL for all other api calls
HOST_URL = "https://cocoapi.bmwgroup.com"

## Bmw Class
# implements BMW API calls
# extends Vehicle Class
class Bmw(Vehicle):
    
    ## Bmw Constructur
    # Read the bmw-csv-file content such as access token, refresh token and metadata
    # than assign their values to the member variables of Bmw class
    def __init__(self,verbose):
        super().__init__(VehConst.BMW_TF_PATH,verbose)
        ## Manufacturer name as String in lowercase "bmw"
        self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
        self.gcid = ""
        self.token_type = ""
        self.scope = ""
        self.expires_in = ""
        self.id_token = ""
        self.argv = ("access_token","refresh_token","gcid","token_type","scope","expires_in","id_token")
        self.setattr_from_csv(*self.argv)
        self.vin = ""
        self.refresh_tokens()

#----------------------------------- API REQUESTS #-----------------------------------
    
    ## API request to get general data on the user and the account
    def get_user_data(self):
        self.logger.url = CUSTOMER_URL +"/protected/v4/mybmwapp/DE-de/customers"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()


    ## API request to get the vehicle(s) linked to the user's account
    def get_vehicles(self):
        self.logger.url =  HOST_URL+"/eadrax-vcs/v1/vehicles?apptimezone=120&appDateTime="+str(int(round(time.time() * 1000)))+"&tireGuardMode=ENABLED"        
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    
    ## build and send request for get charging sessions method
    # user input: month the month for which data is to be requested (1-12)
    # user input: the year for which data is to be requested (example: 2023)
    def get_charging_sessions(self):
        print("Enter start month (1-12): ")
        startm = int(sys.stdin.readline())
        print("Enter end month (1-12): ")
        endm = int(sys.stdin.readline())
        print("Enter year: ")
        year = int(sys.stdin.readline())
        
        data_url = HOST_URL+"/eadrax-chs/v1"
        data_url += "/charging-sessions?vin="+self.vin
        data_url += "&next_token&date="+ str(year)

        self.logger.header = self.get_headers("REQ_HEADERS")

        if(endm - startm >= 0):
            for i in range(startm, endm+1):
                self.logger.url = data_url + "-"+str(i)+"-01T00%3A00%3A00.000Z&maxResults=40&include_date_picker=false"
                self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
                self.logger.log_req_res()
                self.vprint("waiting before next request to avoid account ban")
                time.sleep(2)
        else:
            print("invalid time window")

    ## build and send request for get charging statistics method
    def get_charging_statistics(self):
        self.logger.url = HOST_URL+"/eadrax-chs/v1/charging-statistics?vin="+self.vin+"&currentDate="+str(date.today().strftime("%Y-%m-%d"))+ "T" + str(datetime.now().strftime("%H:%M:%S"))
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header)
        self.logger.log_req_res()

    ## internal helper: make call equivalent to get_vehicles and return the first linked VIN if it exists
    # requires valid access_token
    def __get_vin(self):
        data_url =  HOST_URL+"/eadrax-vcs/v1/vehicles"
        data_url += "?apptimezone=120&appDateTime="+str(int(round(time.time() * 1000)))
        data_url += "&tireGuardMode=ENABLED"
        response = requests.get(data_url, headers=self.get_headers("REQ_HEADERS"))
        if response.status_code != 200 and response.status_code != 207:
            self.vprint("bmw: to get vin access token must be valid")
            return
        res_body = response.json()
        result = json.loads(json.dumps(res_body))
        try:
            self.vin = result[0]["vin"]
            self.vprint(self.__class__.__name__ + " VIN: " + result[0]["vin"])
        except:
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

    ## generate new access token and update the member variabls and bmw-csv-file
    def refresh_tokens(self):
        self.logger.url = TOKEN_URL
        self.logger.header = self.get_headers("TOKEN_HEADERS")
        self.logger.body = self.__get_token_data()
        self.logger.method = "POST"
        self.logger.response = requests.post(self.logger.url, headers=self.logger.header, data=self.logger.body)
        if self.verbose:
            self.logger.log_req_res()
        self.setattr_from_res(self.logger.response,*self.argv)
        self.__get_vin()

    ## generate new access token, refresh token from credentials and update the member variables and bmw-csv-file
    # @param username email
    # @param password password
    # @see ~/docs/drafts/bmw auth.png
    def cred_auth(self, username, password):
        data_first = self.__get_auth_data()
        data_first +="&username="+username
        data_first +="&password="+password
        data_first +="&grant_type=authorization_code"

        session = requests.Session()
        response = requests.post(AUTH_URL, headers=self.get_headers("AUTH_HEADERS"), data=data_first)
        session.cookies.update(response.cookies.get_dict())

        self.vprint("1) Status Code", response.status_code)
        self.vprint("1) Response as Text ", response.text)
        if response.status_code == 200:
            res_body = response.json()
            result = json.loads(json.dumps(res_body))
            authorization = result["redirect_to"].split("&authorization=")[1]
            data_second = self.__get_auth_data()
            data_second +="&authorization=" + urllib.parse.quote(authorization)
            self.vprint("Data_2: ", data_second)

            response_second = requests.post(AUTH_URL, headers=self.get_headers("AUTH_HEADERS"), data=data_second, cookies=session.cookies, allow_redirects=False)
            self.vprint("2) Status Code: ", response_second.status_code)
            self.vprint("2) Response as Text: ", response_second.text)
            self.vprint("2) Response Headers: ", response_second.headers)

            if response_second.status_code == 302:
                headers_second = json.loads(json.dumps(response_second.headers.__dict__['_store']))
                code_third = headers_second["location"][1].split("code=")[1].split("&")[0]
                data_third ="code="+code_third
                data_third +="&redirect_uri=com.bmw.connected://oauth"
                data_third +="&grant_type=authorization_code"
                data_third +="&code_verifier=022578f25b5b5d5194b2b5336d097804e44017d9551072040f1a3955e65ef411"
                self.vprint("Data_3: ", data_third)

                response_third = requests.post(TOKEN_URL, headers=self.get_headers("AUTH_HEADERS_3"), data=data_third, cookies=session.cookies)
                self.setattr_from_res(response_third,*self.argv)
                self.__get_vin()


#----------------------------------- HELPER FUNCTIONS #-----------------------------------

    ## returns the requested HTTP Headers Dictionary of bmw requests
    # example get_headers("TOKEN_HEADERS"), get_headers("AUTH_HEADERS"), get_headers("REQ_HEADERS")
    # @param Name of Dictionary to be returned TOKEN_HEADERS, AUTH_HEADERS, AUTH_HEADERS_3, REQ_HEADERS
    # @return Dictionary of HTTP Headers to send with the request
    def get_headers(self, header):
        headers = {
             "TOKEN_HEADERS": { 
                "x-dynatrace": "MT_3_3_3725343340_21-0_42138ff3-383a-41ca-b4b8-026ff8fd8274_0_311_17",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Authorization": "Basic MzFjMzU3YTAtN2ExZC00NTkwLWFhOTktMzNiOTcyNDRkMDQ4OmMwZTMzOTNkLTcwYTItNGY2Zi05ZDNjLTg1MzBhZjY0ZDU1Mg==",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-G965F Build/TD1A.220804.031)",
                "Connection": "Keep-Alive"
                },
            "AUTH_HEADERS": { 
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1",
                "Accept-Language": "de-de"
                },
            "AUTH_HEADERS_3": { 
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "User-Agent": "My%20BMW/8932 CFNetwork/978.0.7 Darwin/18.7.0",
                "Accept-Language": "de-de",
                "Authorization" : "Basic MzFjMzU3YTAtN2ExZC00NTkwLWFhOTktMzNiOTcyNDRkMDQ4OmMwZTMzOTNkLTcwYTItNGY2Zi05ZDNjLTg1MzBhZjY0ZDU1Mg=="
                },
            "REQ_HEADERS": {
                    "Authorization" : "Bearer "+self.access_token,
                    "Accept-charset" : "UTF-8",
                    "x-user-agent" : "android(SP1A.210812.016.C1);bmw;99.0.0(99999);row"
            }
        }
        return headers[header]
    
    ## returns the x-www-form-urlencoded body for the refresh_token request
    # requires valid access_token
    # @return x-www-form-urlencoded body for refresh_tokens
    def __get_token_data(self):
        data ="refresh_token=" + self.refresh_token
        data +="&grant_type=refresh_token"
        data +="&scope=openid+profile+email+offline_access+smacc+vehicle_data+perseus+dlm+svds+cesim+vsapi+remote_services+fupo+authenticate_user"
        data +="&redirect_uri=com.bmw.connected://oauth"
        return data
    
    ## returns the x-www-form-urlencoded body for the cred_auth request
    # @return x-www-form-urlencoded body for cred_auth
    def __get_auth_data(self):
        data ="client_id=31c357a0-7a1d-4590-aa99-33b97244d048"
        data +="&response_type=code"
        data +="&scope=openid profile email offline_access smacc vehicle_data perseus dlm svds cesim vsapi remote_services fupo authenticate_user"
        data +="&redirect_uri=com.bmw.connected://oauth"
        data +="&state=cwU-gIE27j67poy2UcL3KQ"
        data +="&nonce=-hprPzIXltsh4g_9LT7m4g"
        data +="&code_challenge_method=S256"
        data +="&code_challenge=czpYBFGjqgIdxZChNokBsEsC03KIoDMuofMRv01hy2U"
        return data