import json
import yaml
import hashlib
import inspect
from datetime import datetime
from VehConst import VehConst

## Class LogReqs serves the purpose of logging and hashing requests and responses to json (or yaml) files
# before sending a request the logger attributes (as listed in constructor) need to be set accordingly
# if attributes are not set, output in the logs is going to be empty

class LogReqs:
    ## constructor intializes method with "GET" so that it does not have to be specified to many of the requests
    # verbose value is passed for use in vprint
    def __init__(self, verbose):
        self.method = "GET"
        self.mf_name = ""
        self.url = ""
        self.header = ""
        self.body = ""
        self.response = None
        self.verbose = verbose

    ## should be called after each request that needs to be logged, collects all neccessary data and logs it to a csv-file
    # resulting file names look like this: YYYY-MM-DD_HH-MM-SS_manufacturer_api_call_{response|info}.json. example: 2023-04-28_18-14-49_bmw_get_charging_statistics_response.json
    # relevant attributes such as url, header, body and response have to be set by the caller beforehand
    # method parameter is set to 'GET' in constructor by default and only needs to be explicitly specified if a different HTTP method is intended to be used
    def log_req_res(self):
        if(self.response == None):
            print("Error Response is not initialized")
            return
        req_name = self.mf_name + "_" + inspect.stack()[1].function
        self.print_response()
        # datetime object containing current date and time
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")

        timestamp_fname = VehConst.LOG_PATH+dt_string+"_"+req_name
        json_res_headers = json.loads(json.dumps(dict(self.response.headers), sort_keys=True, indent=4))
        http_version = 'HTTP/'+str(self.response.raw.version)
        
        #create response json
        res_file = {
            'HTTP version': http_version,
            'Status code': str(self.response.status_code),
            'Reason phrase': str(self.response.reason),
            'HTTP headers': json_res_headers,
            'Message body': self.get_response()
        }
        #sha-256 hash value of response
        hash_res = self.hash_of_response(str(json.dumps(res_file, indent=4)))

        #create info json
        json_info = {
            'HTTP method': str(self.method),
            'Path': str(self.url),
            'HTTP version': http_version,
            'JsonResponse-Hash': str(hash_res)
        }
        json_req = {
            'HTTP headers': self.header,
            'Message body': self.body
        }
        info_file = {
            'Info': json_info,
            'Request': json_req
        }

        #create info files (json/yml)
        info_file_name = timestamp_fname+"_info"
        f_info= open(info_file_name+".json","w+")
        f_info.write(json.dumps(info_file, indent=4))
        f_info.close()
        #self.convert_json_to_yaml(info_file,info_file_name)
        #create response files (json/yml)
        res_file_name = timestamp_fname+"_response"
        f_res= open(res_file_name+".json","w+")
        f_res.write(json.dumps(res_file, indent=4))
        f_res.close()        
        #self.convert_json_to_yaml(res_file,res_file_name)

    ## currently unused, converts the json logs to yaml format
    def convert_json_to_yaml(self,json_data, file_name):
        f = open(file_name+".yml", 'w+')
        f.write(yaml.dump(json_data, sort_keys=False, allow_unicode=True))
        f.close()

    ## calculate and return the sha256 hash of the given response 
    # @param response_str the response returned by an API as string
    # @return sha256 hash as hexadecimal string
    def hash_of_response(self, response_str):
        result = hashlib.sha256(response_str.encode('UTF-8'))
        return result.hexdigest()
    
    ## print responses returned by APIs and print error message if requests was unsuccessful
    # output also depends on value of "self.verbose"
    # @return the response as json on success, empty string on error
    def print_response(self):
        res = ""
        self.vprint("Status Code: "+str(self.response.status_code))
        if self.response.status_code != 200 and self.response.status_code != 207:
            res = self.response.text
            # determine manufacturer where the error occured by using inspect.stack to get the name of the class that called the logger
            # index 1 would return stack frame of caller log_req_res() so index has to be 2
            print(f"{inspect.stack()[2].frame.f_locals.get('self', None).__class__.__name__}: API error - most likely invalid token or insufficient vehicle capabilities")
        else:
            res = self.response.json()
            print(res)
        return res

    ## return response body   
    # @return response.body as json on successful request, else response.text
    def get_response(self):
        res = ""
        if self.response.status_code != 200 and self.response.status_code != 207:
            res = self.response.text
        else:
            res = self.response.json()
        return res

    ## prints args if self.verbose is true
    # @param *args variable length list of args to be printed
    def vprint(self,*args):
        if(self.verbose):
            print(args)


