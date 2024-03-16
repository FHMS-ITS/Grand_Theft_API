from getpass import getpass
import sys
import Menu as menu

## reads user input in a loop and calls manufacturer's api functions accordingly
def mercedes_requests(mercedes):
    while True:
        req = menu.print_mercedes_requests()
        if req == 'b':
            return mercedes
        elif req == '0':
            new_access_token(mercedes)
        elif req == '1':
            mercedes.get_vehicles_iobroker()
        elif req == '2':
            mercedes.get_vehicles_app()
        elif req == '3':
            mercedes.get_consumption()
        elif req == '4':
            mercedes.get_capabilities()
        else:
            print("unknown Request")

## reads user input in a loop and calls manufacturer's api functions accordingly
def bmw_requests(bmw):
    while True:
        req = menu.print_bmw_requests()
        if req == 'b':
            return bmw
        elif req == '0':
            new_access_token(bmw)
        elif req == '1':
            bmw.get_user_data()
        elif req == '2':
            bmw.get_vehicles()
        elif req == '3':
            bmw.get_charging_sessions()
        elif req == '4':
            bmw.get_charging_statistics()
        else:
            print("unknown Request")

## reads user input in a loop and calls manufacturer's api functions accordingly
def audi_requests(audi):
    audi.vin = input("Enter Audi Vin:")
    while True:
        req = menu.print_audi_requests()
        if req == 'b':
            return audi
        elif req == '1':
            audi.get_vehicles()
        elif req == '0':
            new_access_token(audi)
        else:
            print("unknown Request")

## reads user input in a loop and calls manufacturer's api functions accordingly
def ford_requests(ford):
    while True:
        req = menu.print_ford_requests()
        if req == 'b':
            return ford
        elif req == '1':
            ford.get_user_data()
        elif req == '2':
            ford.get_expdashboard_details()
        elif req == '3':
            ford.get_vehicles_status()
        elif req == '0':
            new_access_token(ford)
        else:
            print("unknown Request")

## reads user input in a loop and calls manufacturer's api functions accordingly
def hyundai_requests(hyundai):
    while True:
        req = menu.print_hyundai_requests()
        if req == 'b':
            return hyundai
        elif req == '1':
            hyundai.get_vehicles()
        elif req == '2':
            hyundai.get_user_profile()
        elif req == '0':
            new_access_token(hyundai)
        else:
            print("unknown Request")

## reads user input in a loop and calls manufacturer's api functions accordingly
def renault_request(renault):
    while True:
        req = menu.print_renault_requests()
        if req == 'b':
            return renault
        elif req == '0':
            new_access_token(renault)
        elif req == '1':
            renault.get_user_data()
        elif req == '2':
            renault.get_vehicles()
        elif req == '3':
            renault.get_battery_status()
        elif req == '4':
            renault.get_battery_inhibition_status()
        elif req == '5':
            renault.get_cockpit("v2")
        elif req == '6':
            renault.get_charge_mode()
        elif req == '7':
            renault.get_hvac_status()
        elif req == '8':
            renault.get_hvac_settings()
        elif req == '10':
            renault.get_charge_history()
        elif req == '9':
            renault.get_charging_settings()
        elif req == '11':
            renault.get_charges()
        elif req == '12':
            renault.get_lock_status()
        elif req == '13':
            renault.get_res_state()
        elif req == '14':
            renault.get_location()
        else:
            print("unknown Request")

## lets the user enter tokens manually, or generate them by using user credentials or a refresh_token
# first a menu is printed and user input is read
# then the correct auth_requests for the manufacturer is called
# @param manufac the manufacturer's class instance
def new_access_token(manufac):
    print("Type:")
    print("0: Enter user credentials (except Audi, Hyundai, Ford)")
    print("1: Enter access token")
    print("2: Enter refresh token")
    print("3: Generate access token by using existing refresh token")
    
    cnd_t=int(sys.stdin.readline())
    if cnd_t == 0 :
        username = input("Enter email / username: ")
        while len(username) < 5:
            print("No email / username entered")
            username = input("Enter email / username: ")
        if(manufac.mf_name == "mercedes"):
            manufac.get_pin(username)
        password = getpass("Enter password / pin: ")
        while len(password) < 5:
            print("No password / pin entered")
            password = getpass("Enter password / pin: ")
        manufac.cred_auth(username,password)

    if cnd_t == 1 :
        new_token = input("Enter new access token: ")
        if len(new_token) == 0:
            print("No access token entered")
            return
        manufac.set_access_token(new_token)
    
    if cnd_t == 2 :
        new_token = input("Enter new refresh token: ")
        if len(new_token) == 0:
            print("No refresh token entered")
        manufac.set_refresh_token(new_token)

    if cnd_t == 3 :
        manufac.refresh_tokens()
