Description
=======

This module collects statistical data of college plaeyrs who were drafted since the 1930's. The data is collected from
Sports Reference:
https://www.sports-reference.com/cfb/

It creates the following json files to store raw college data:
In the format of player_dict.json
In the format of player_dict-college-withCareerwithYear.json

It creates the following CSV files to store college statistics:
In the format of all_<stat_group>.csv

It creates the following CSV file to store drafted by data:
In the format of draftedBy.csv

## System Requirements
Anaconda3 - Jupyter Notebook
Python 3

## Python Library Requirements
requests
string
bs4
time
pprint
json
random
re
pandas
numpy
matplotlib 

## Instructions

Code broken down into the following files.  Each part will take time to run and can be started again picking up where it left off.  Files need to be ran in order as each part is dependent on the outputs of the previous part.  Files will scrape sports-reference.com and store the data into raw nested objects and then saved to json files.

1 - "Crawler-p1-getCollegeLinks.ipynb"
2 - "Crawler-P2-getProLinks.ipynb"
3 - "Crawler-P3-getStats.ipynb"

Once the first three parts are run, there will be a completed json file called "player_dict-college-withCareerwithYear.json".  This file is a dependency for the transformer code to convert the data from raw Key:value storage into a tabular format that can be saved to CSV.  The final output will generate four CSV files.  One for passing, one for offensive skill position players, and one for defensive players.  The final fourth CSV will be a file that contains draft information for each player.

4 - "CollegeTransformer.ipynb"

## College EDA for statistical Analysis

College EDA notebook available for review.  Current analysis done with two anbalyses in mind.  First analysis is on college offensive production overtime.  Assesing whether there is noticble trends since 1980 in offensive production in College.  The second analysis is to assess the strength of conferences on the basis of how many players are drafted to the NFL per conference.  Furthering looking at which rounds players were selected.  The goal is to identify trends in which conferences have more or less players selected in which rounds.

"CollegeEDA.ipynb"

## College Data Definitions

Please navigate to the following file for more information on the data definitions for the college statistics.

"College Data Definitions.xlsx"
