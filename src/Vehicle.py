import csv
import abc
import os
import requests
import json
from  LogReqs import LogReqs
from VehConst import VehConst


## abstract class used as superclass for manufacturer classes
# includes a number of abstract methods (@abc.abstractmethod) that need to be implemented in each manufacturer's class
class Vehicle:
    
    ## constructor that will be called in the subclasses
    # @param verbose verbose flag is given by subclass and passed on to LogReqs
    # @param tokens_path tokens_path also given by subclass
    def __init__(self, tokens_path, verbose):
        ## path of csv configuration file
        self.tokens_path=tokens_path
        ## Manufacture name
        self.mf_name = ""
        self.access_token = ""
        self.refresh_token = ""
        self.verbose = verbose
        self.logger = LogReqs(verbose)

    ## following abstract functions have to be implemented in each subclass, for examples on how to implement check documentation of Template.py

    ## set the member variable access_token
    # and then calls the function update_csv to update the csv-file
    @abc.abstractmethod
    def set_access_token(self, access_token):
        self.access_token = access_token
    
    ## set the member variable refresh_token
    # and then calls the function refresh_tokens to acquire new tokens
    @abc.abstractmethod
    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token
    
    ## Function for generating access token using refresh token
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response
    # and call setattr_from_res(self.logger.response,*self.argv) *self.argv is set in constructor 
    # setattr_from_res sets the member variables of the class by reading new values from the response 
    # setattr_from_res also updates the csv file by calling update_csv internally
    @abc.abstractmethod
    def refresh_tokens(self):
       print("Method refresh_tokens must be implemented by "+ self.mf_name + " to refresh tokens and update csv file")

    ## Function for generating access token, refresh token from credentials
    # set necessary info for logging using self.logger from LogReqs  
    # generate the request, set the response and call log_req_res() to log the request and response
    # and call setattr_from_res(self.logger.response,*self.argv) *self.argv is set in constructor 
    # setattr_from_res sets the member variables of the class by reading new values from the response
    # setattr_from_res also updates the csv file by calling update_csv internally
    # @param username email
    # @param password password
    @abc.abstractmethod
    def cred_auth(self, username, password):
         print("Method cred authentication must be implemented by " + self.mf_name)

    ## Function for setting attributes given in argv by reading them from csv
    # @param *argv caller gives the names of the attributes as string. Example: argv = ("access_token","refresh_token","expires_in","refresh_expires_in")
    # attributes included in argv that do not exist in the csv file are ignored
    def setattr_from_csv(self, *argv):
        ## if csv do not exist create new one with None as values of attribute
        if (os.path.exists(self.tokens_path) == False):
            with open(self.tokens_path, mode ='x') as new_file:
                csvwriter = csv.writer(new_file, delimiter = ";")
                for arg in argv:
                    csvwriter.writerow( (arg, "None"))
            return
        ## if csv file exists open and read in dictionary tokens with keys and values
        tokens = {}
        with open(self.tokens_path, mode ='r') as file:
            csvFile = csv.reader(file, delimiter = ";")
            for line in csvFile:
                if(len(line)==2):
                    tokens[line[0]] = line[1]
        for arg in argv:
            if arg in tokens:
                setattr(self,arg,tokens[arg])
    
    ## Function for setting attributes given in argv by extracting them from a HTTP response
    # @param response an API's response as received by python.requests
    # @param *argv caller gives the names of the attributes as string. Example: argv = ("access_token","refresh_token","expires_in","refresh_expires_in")
    # attributes included in argv that do not exist in the HTTP response are ignored
    def setattr_from_res(self, response: requests.Response, *argv):
        self.vprint("Status Code: ", response.status_code)
        self.vprint("JSON Response: ", response.json())
        if response.status_code == 200:
            data = response.json()
            result = json.loads(json.dumps(data))
            self.vprint(result)
            for arg in argv:
                if arg in result:
                    setattr(self,arg,result[arg])
            self.update_csv(*argv)


    ## Function for updating the manufacturer's csv file
    # @param *argv caller gives the names of the attributes as string. Example: argv = ("access_token","refresh_token","expires_in","refresh_expires_in")
    def update_csv(self, *argv):
        tokens = {}
        with open(self.tokens_path, mode ='r') as file:
            csvFile = csv.reader(file, delimiter = ";")
            for line in csvFile:
                if(len(line)==2):
                    tokens[line[0]] = line[1]

        with open(VehConst.TEMP_PATH, mode ='x') as new_file:
            csvwriter = csv.writer(new_file, delimiter = ";")
            for arg in tokens:
                if arg in argv:
                    csvwriter.writerow( (arg, getattr(self,arg)))
                else:
                    csvwriter.writerow( (arg, tokens[arg]))
                    
        if os.path.exists(VehConst.TEMP_PATH):
                os.rename(VehConst.TEMP_PATH, self.tokens_path)
                self.vprint(self.mf_name+" csv-token-file was successfully updated")
        else:
                print("The file does not exist")

    ## Function to only print debug info if verbose is set to True
    def vprint(self,*args):
        if(self.verbose):
            print(args)