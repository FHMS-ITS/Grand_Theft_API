## print list of supported manufacturers
def print_manufac():
    print("\n\nTo Exit: 0")
    print("MERCEDES: 1")
    print("BMW: 2")
    print("AUDI: 3")
    print("FORD: 4")
    print("HYUNDAI: 5")
    print("RENAULT: 6")
    print("DACIA: 7")
    print("")

## print list of supported Mercedes API requests
def print_mercedes_requests():
    print("\n\nvehicles (iobroker): 1")
    print("vehicles (app): 2")
    print("consumption: 3")
    print("capabilities: 4")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")

## print list of supported Bmw API requests
def print_bmw_requests():
    print("\n\nuser data: 1")
    print("vehicles: 2")
    print("charging sessions: 3")
    print("charging statistics: 4")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")

## print list of supported Audi API requests
def print_audi_requests():
    print("\nvehicles: 1")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")

## print list of supported Ford API requests
def print_ford_requests():
    print("\n\nuser data: 1")
    print("expdashboard details: 2")
    print("vehicle status: 3")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")

## print list of supported Hyundai API requests
def print_hyundai_requests():
    print("\n\nvehicles: 1")
    print("user profile: 2")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")

## print list of supported Renault API requests (also used for Dacia)
def print_renault_requests():
    print("\n\nuser data: 1")
    print("vehicles: 2")
    print("battery status: 3")
    print("battery inhibition status: 4")
    print("cockpit: 5")
    print("charge mode: 6")
    print("hvac status: 7")
    print("hvac settings: 8")
    print("charging settings: 9")
    print("charge history: 10")
    print("charges: 11")
    print("lock status: 12")
    print("res state: 13")
    print("location: 14")
    print("enter token: 0")
    print("back to menu: b")
    print("")
    return input("Choose Request: ")