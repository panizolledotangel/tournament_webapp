# aco_competi

This repository contains code for a web app to do tournaments. During a tournament contestants must compete to solve a TSP (traveling salesman problem). The tournaments uses google drive to read the solutions of the contestants and shows the results in a ranking via web. The ranking is periodically updated automatically.

## Pre-requisites

The app is dockerized so only *docker* and *docker-compose* are needed.

## Setup for a new tournament

To organize a new tournament you need to follow the next steps.

1. **Google drive credentials setup**: Some configurations need to be done in your google account in order to generate the **credentials.json** file that will allow the app to read data from your google drive. Follow steps 1-7 of this [tutorial](https://obikastanya.medium.com/easy-way-to-integrate-your-python-apps-with-google-drive-api-2f29ed0be239).

2. **Setup google drive folder**: Create a folder in your google drive where the tournament data will be read. Save the **id of the folder** for later, the id is the last part of the url of your google drive folder (ej. https://drive.google.com/drive/folders/**XXXXXYYYXXXYYXXX**)

3. **Create a folder for each contestant**: Inside the google drive folder created in the previous step, create one folder for each contestant. The name of the folder will be the name shown in the ranking. Share the folder with the contestant so he/she can put files into that folder.

4. **Create a .tsp file**: This file will define the TSP problem that needs to be solved by the contestants. More information about .tsp format and tsp files examples can be found [here](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/).

5. **Configure the app**: Create a *.env* file in the root of this repository with the next fields:

```
# Name of your tournament
TOURNAMENT_NAME=
# tsp file obtained in step 4, needs to be in the root of the repository
PROBLEM_FILE=
# initial score for all contestants in the tournament
INITIAL_SCORE=
# id obtained in step 2,
ROOT_FOLDER_ID=
# file with the credentials to access your google drive, created at step 1
GOOGLE_CREDENTIALS_FILE=
# path to a folder where a log of the tournament will be saved
RANKING_FOLDER_PATH=
# Port where the web with the ranking is available
FLASK_PORT=
```

6. **Start the application**: Run `docker-compose up` to start the application. Once everything is ready the application will be accesible at *http://localhost:{FLASK_PORT}*

## How the tournament works

Once the webapp is started the contestants will be automatically configured. There will be one contestant for each of the folder created in the step 3 of the setup. **WARNING: No more contestants are allowed to enter after this point**.

### Send a solution

Contestants can send a solution by putting a .json file with the next structure inside their folder.

```json
{
    "solution":[0,1,2,3]
}
```

The file must have one unique key (*"solution"*) that containts a list of intergers that indicates the order in which the cities of the TSP problem will be visited. One city can only appear one time in the arrive, from the last city the path will travel to the first city. For example, the array *[0,1,2,3]* indicates the next path: 0->1->2->3->0 (i.e we start on city cero then visit cities 1,2 and 3 in that order, and finally go from 3 to 0).

The folder can have several .json files, however the system will only read the most recent one.

### Ranking update

**The ranking web updates automatically asynchronously every 10 seconds so no refresh is needed**

Each minute the application will check the google drive to check if any contestants have updated their folder. If so, the system will calculate the score of the solution and update the ranking acordingly. 

All contestants start with the default value and a *PENDING* state (⏳). Once they put a .json file in their folder and the system read it, the state of a contestant will change to *OK* (✅). The ranking shows the length of the last solution submitted as well as the best score submmit so far during the whole tournament.

If the system encounters error while processing a contestant's solution, the contestant will be marked as *ERROR* (❌). More information about the error can be found at *http://localhost:{FLASK_PORT}/statuses*
