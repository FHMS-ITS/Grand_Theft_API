![Grand Theft API](./docs/drafts/logo.png)

## Getting started 
 - [DFRWS EU 2024 Paper](https://doi.org/10.1016/j.fsidi.2023.301691) - Corresponding paper 
 - [doxygen](./docs/html/index.html) - Documentation for source code
 - [config](./config) - Config files such as token-csv-files and other constants
 - [logs](./logs) - Default location for logging of requests
 - [src](./src) - gta.py source code

 ## Installation

Use pip to install the requirements.txt

```bash
pip install -r requirements.txt
```
or
```bash
python3 -m pip install -r requirements.txt
```

then create the required directories by executing the bash script requiredDir.sh
the directories needed are listed in VehConst.py and can be changed if desired

```bash
./requiredDir.sh
```

first navigate to the src directory, then start the gta.py script
paths for csv files are relative to /src, so executing must be done from inside /src

```bash
cd src
./gta.py -v
```

## Contribution 

We are open to all kinds of contributions. If it's a bug fix or a new feature, feel free to create a pull request. 
Please consider some points:
 - Just include one feature or one bugfix in one pull request. In case you have two new features please also create two pull requests.
 - Try to stick with the code style used. 

Nice to know:
 - [drafts](./docs/drafts) - Flow diagrams, images and architecture 
 - [README Extensibility](./docs/README.md) - README file on how to extend gta.py
