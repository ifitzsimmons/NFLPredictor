Description
=======

This module collects statistical data of every player drafted in the
NFL in the last 20 years, excluding rookies. The data is collected from
Pro Football Reference:
https://www.pro-football-reference.com/years/{year}/draft.htm.

It creates a CSV file
In the format of <start_year>_<end_year>.csv

## Requirements
To run this script you will need at least Python 3.6

## Instructions

If Python 3 is installed
```console
$ python -m get_draft_results_and_stats.py
```

This will collect all the data for players drafted in the last 20 years.
It will write the data to the `ProData/results` folder and will write `json` files for each draft. It splits the files for each draft base on the first initial of the player's last name.

The next step would be to run the following command:
```console
$ python -m clean_and_split_data.py
```

This will take the raw data collected in the first step and organize it. It will create a `ProData/cleaned` directory with subfolders for different data categories
1. Combine Data
2. Career Data with season-by-season metrics.
3. Draft Data
4. Career Awards data.

To convert data to csv format, run the following"
```console
python -m make_csv.py
```

This will generate Three CSV files, one for each position category
1. Quarterbacks
2. Skill Players (RBs, WR, FBs, and TEs)
3. Defense (all defensive players)
