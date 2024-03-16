import requests
from datetime import datetime, timezone

FREQUENCY = 120

## Scipt to get current BlueLinkyStamp from a open source git repo
# stamps are used for Hyundai and Kia
# every 4 hours the repo is automatically updated with sets of fresh bluelinky stamps
# to use this script for Kia, some changes are necessary, because "path_to_file" is specific to hyundai
def get_bluelinky_stamp(verbose):
    DEBUG = verbose
    if(DEBUG):
        print("### get_bluelinky_stamp")
    path_to_file = '/master/hyundai-014d2225-8495-4735-812d-2616334fd15d.json'
    url = f'https://api.github.com/repos/neoPix/bluelinky-stamps/commits?/commits?path={path_to_file}&per_page=1'

    response = requests.get(url, headers=None)

    #calculate age of latest commit
    if response.status_code == 200:
        commit_timestamp = response.json()[0]['commit']['committer']['date']
        commit_datetime = datetime.fromisoformat(commit_timestamp.replace('Z', '+00:00'))
        current_datetime = datetime.now(timezone.utc)
        time_diff = current_datetime - commit_datetime
        if(DEBUG):
            print(f'Last commit timestamp: {commit_timestamp}\n')
            print(f'Time difference between current time and last commit timestamp for file {path_to_file}: {time_diff}')
    else:
        print(f'Error: {response.status_code}')

    #get content of latest hyundai stamps
    url = 'https://raw.githubusercontent.com/neoPix/bluelinky-stamps/master/hyundai-014d2225-8495-4735-812d-2616334fd15d.json'
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        if(DEBUG):
            print("\nGot stamps json from github\n")
    else:
        print(f'Request failed with status code {response.status_code}')
        exit(1)
    
    #calculate offset for currently valid stamp based on age and frequency
    stamp_offset = int((time_diff.total_seconds()/FREQUENCY)-1)
    if(DEBUG):
        print("Calculated stamp offset based on 120 seconds validity:\nstamps[" + str(stamp_offset)+"]:")
    stamp = json_data[stamp_offset]
    if(DEBUG):
        print(stamp)
    return stamp


