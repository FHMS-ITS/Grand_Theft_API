# Extensibility of gtapy tool

The gtapy tool is designed to be easily extensible, allowing for uncomplicated integration of new manufacturers' APIs. Once the API for a desired manufacturer is known, adding support for that manufacturer in the tool is a straightforward process. The following steps are all that is needed to add a new manufacturer to the tool.
A template is used to explain how to integrate new manufacturers.

## Editing VehConst.py

Add an entry for the new manufacturer csv file in VehConst.py, where the tokens that we get from authentication requests are store. such as access token and refresh token

```python
TEMPLATE_TF_PATH = '../config/template_tokens.csv'
```

## Adding new Class

Create a new class named after the manufacturer as a subclass of Vehicle, or clone the Template.py class and rename it after the manufacturer then edit the class according to requirements

### First section

Add URLs for API requests as constants outside or inside the new class

```python
## Constant URL for generating an access token (using refresh token)
TOKEN_URL = "https://template-token.com"
## Constant URL for authentification with credentials
AUTH_URL = "https://template-oauth.com"
## Constant URL for all other api calls
HOST_URL = "https://template-host.com"
```

### Define the __init__() method (constructor)

the first think to do in __init__() method is calling the super.__init__() method of the abstract class Vehicle.py with the path of csv file that we define in VehConst.py and pass the VERBOSE flag to Vehicle.py class

```python
super().__init__(VehConst.TEMPLATE_TF_PATH,verbose)
```

or

```python
self.mf_tf_path = self.__class__.__name__.upper() + "_TF_PATH"
super().__init__(getattr(VehConst, self.mf_tf_path), verbose)
```
- then you need to intitilaze the two member varibles self.mf_name, self.logger.mf_name of Vehicle.py with the name of manufacturer in lower case
- then you need to set self.argv with all response's attributes from cred_auth and refresh_tokens methods that are needed for integration of manufacturers' APIs
- the call the setattr_from_csv method ,it is defined in Vehicle.py, it read the csv-file and sets the member variable that are given as parameter from the values within the csv file
- optional you could call refresh_tokens method to refresh the tokens at the beginning if they are expired

```python
# Manufacturer name as String in lowercase "template"
self.mf_name = self.logger.mf_name = self.__class__.__name__.lower()
## access_token, refresh_token, template_token1 ... are the refresh_tokens and cred_auth response's attributes 
self.argv = ("access_token","refresh_token","template_token1","template_token2")
self.setattr_from_csv(*self.argv)
self.refresh_tokens()
```

### API REQUESTS section

Implement API requests for data acquisition in the API REQUESTS section, the folowing function is an example from Template.py, it demonstrate how to log and send requests

```python
def get_ressource_template(self):
        self.logger.url = HOST_URL +"/ressource"
        self.logger.header = self.get_headers("REQ_HEADERS")
        self.logger.body = "data_template"
        self.logger.response = requests.get(self.logger.url, headers=self.logger.header, data=self.logger.body)
        self.logger.log_req_res()
```

if you want to log the request and response of this api call, you need to set the logger member variables
 - method has a default value "GET" because the most calls are get requests, it can be sets as post or other method 'self.logger.method = "POST"'
 - mf_name is allready set in Vehicle.py
 - url is the url "Host + url of data acquisition" of the api request
 - header is the headers of the api request
 - body is the data or json that are send as body with the api request
 - response is the response form the api request
 - verbose is allready set in Vehicle.py
then call log_req_res to print and log the request and response

```python
def __init__(self, verbose):
        self.method = "GET"
        self.mf_name = ""
        self.url = ""
        self.header = ""
        self.body = ""
        self.response = None
        self.verbose = verbose
```

### AUTH REQUESTS section

Implement authorization requests for in the AUTH REQUESTS section, this section have at least four function

 - set the member variable refresh_token and then calls the function refresh_tokens to acquire new tokens
 - set the member variable access_token and then calls the function update_csv to update he csv-file
 - generating access token using refresh token and call log_req_res() to log the request and response then setattr_from_res sets the member variables of the class by reading new values from the response setattr_from_res also updates the csv file by calling update_csv internally
 -  generating access token, refresh token from credentials and call log_req_res() then setattr_from_res()

```python
def set_refresh_token(self, refresh_token):

def set_access_token(self, access_token):

def refresh_tokens(self):

def cred_auth(self, username, password):
```

### HELPER FUNCTIONS section

Additionally, helper functions can be included, which are not strictly necessary but can prove useful for recurring tasks such as parameter validation or updating variables and CSV files.

## Editing Menu,py 

Add a function named print_manufacturer_requests() to Menu.py, the folowing function is an example for Template.py in Menu.py

```python
def print_template_requests():
    print("\n\n ressource template: 1")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")
```

## Editing ReqCreator.py

Add a function named manufacturer_requests() to ReqCreator.py, the folowing function is an example for Template.py in ReqCreator.py

```python
def template_requests(template):
    while True:
        req = menu.print_template_requests()
        if req == 'b':
            return template
        elif req == '0':
            new_access_token(template)
        elif req == '1':
            template.get_ressource_template()
        else:
            print("unknown Request")
```

## Last step edit gta.py

In gta.py:
 - Import the newly created class
 - Initialize the manufacturer object and pass it the VERBOSE flag
 - Add an entry in the main "Choose manufacturer" loop
The folowing code sections is an example for Template.py in gta.py

```python
from Dacia import Dacia
###
template = Template(VERBOSE)
###
###
    elif manufac == 'X':
        template = RC.template_requests(template)
```