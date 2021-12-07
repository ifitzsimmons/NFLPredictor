import os
from collections import defaultdict
import json
from typing import DefaultDict
import pandas as pd

defense = ['DB', 'DE', 'DL', 'DT', 'LB', 'S']
skill_positions = ['FB', 'RB', 'TE', 'WR']
quarterback = 'QB'

def get_json_data(root, file):
  with open(f'{root}/{file}', 'r') as season_stats_data_file:
    season_stats = json.load(season_stats_data_file)
  return season_stats

def write_json_to_csv(data, csv_file_path):
  csv_data_frame = pd.DataFrame(data)
  csv_data_frame.to_csv(csv_file_path)

def get_list_of_nones_for_data(entry_count: int, len_of_items: int):
  '''
  Returns a list of Nones used to fill in column data.

  Args:
    entry_count: Total number of season rows in the dataset.
    len_of_items: Total number of items in a given "column"

  Returns:
    List[None] - List of None's that will catch the column up to the
      total number of entries

  Examples:
    >>> get_list_of_nones_for_data(10, 5)
    [None, None, None, None, None]
  '''
  missing_vals = entry_count - len_of_items
  return [None for _ in range(missing_vals)]

def prepare_for_csv(data: dict, entry_count: int, season_stats: dict):
  '''
  Prepares data for csv conversion

  This data is schemaless. Some players will have certain columns while others do not.
  This function will fill missing values with None when a new stat type is introduced
  to the dataset.

  This allows the data to be easily written to a csv.

  Args:
    data: csv-ready data structure for a player for a season
    entry_count: Number of total seasons prepared for CSV format so far.
    season_stats: Any given season statistic object

  Returns:
    data: csv-ready data structure for a player for a season

  Examples:
    In this example, there are 3 total keys in the dataset, but no two seasons have the same key.
    The final data structure should have 3 keys, each with values that are lists of equal length.
    If a season (or seasons) did not include a key that was previously introduced or has just been
    introduced to the dataset, the function will add None for those seaons missing the key.

    Given seasons:
      {'key1': 1, 'key2': 1}
      {'key1': 2}
      {'key2': 3, 'key3': 3}

    The return structure should look like
      {
        'key1': [1, 2, None],
        'key2': [1, None, 3],
        'key3': [None, None, 3]
      }
    >>> prepare_for_csv(defaultdict(list), 0, [{'key1': 1, 'key2': 1}, {'key1': 2}, {'key2': 3, 'key3': 3}])
    (3, defaultdict(<class 'list'>, {'key1': [1, 2, None], 'key2': [1, None, 3], 'key3': [None, None, 3]}))
  '''
  for player_data in season_stats:
    for key, value in player_data.items():
      if key not in data and entry_count != 0:
        # if 3 players have been added and the 4th introduces a new key,
        # create a list of Null of length three for the key and append the value
        # of the 4th player
        data[key] = [None for _ in range(entry_count)]
      elif len(data[key]) != entry_count:
        # If the key does not have as many entries as the other keys
        data[key].extend(get_list_of_nones_for_data(entry_count, len(data[key])))

      data[key].append(value)

    # The entry count represents the number of players entered for this key
    entry_count += 1

    for key, list_of_items in data.items():
      if len(list_of_items) != entry_count:
        # Handle case where the last entry is missing known keys
        data[key].extend(get_list_of_nones_for_data(entry_count, len(list_of_items)))

  return entry_count, data

def validate_csv_dictionary(csv_prepped_data: DefaultDict[str, list]):
  '''
  Asserts that each column in the dataset has the same number of entries

  Args:
    csv_prepped_data: Dictionary that has been prepped for CSV write.
      String to list mappings where the string is the column name and the list
      contains data by row for the column.

  Raises:
    AssertionError: If there are no rows or the columns do not have equal number of entries.

  Examples:
    >>> validate_csv_dictionary({'key1': ['1', None], 'key2': [None, 2]})

    >>> validate_csv_dictionary({'key1': [], 'key2': [1]})
    Traceback (most recent call last):
    ...
    AssertionError

    >>> validate_csv_dictionary({'key1': [1, 2], 'key2': [1]})
    Traceback (most recent call last):
    ...
    AssertionError: Key, key2, is missing data. Expected Entries = 2, Actual Entries = 1
  '''
  number_of_entries = 0

  for key, list_of_items in csv_prepped_data.items():
    if number_of_entries == 0:
      number_of_entries = len(list_of_items)

    assert(number_of_entries != 0)
    assert(number_of_entries == len(list_of_items)), (
      f'Key, {key}, is missing data. Expected Entries = {number_of_entries},'
      f' Actual Entries = {len(list_of_items)}'
    )

if __name__ == '__main__':
  '''
  Parses cleaned data and writes it to CSV based on position category:
    1. Quarterback CSV
    2. Skill Position CSV
    3. Defense CSV
  '''
  defense_stats = defaultdict(list)
  skill_player_stats = defaultdict(list)
  qb_stats = defaultdict(list)
  defensive_entries = 0
  skill_entries = 0
  qb_entries = 0

  for root, _, files in os.walk('./ProData/cleaned/season_stats'):
    *_, position = root.split('/')
    for file in files:
      season_stats = get_json_data(root, file)
      if position in defense:
        defensive_entries, _ = prepare_for_csv(defense_stats, defensive_entries, season_stats)
      elif position in skill_positions:
        skill_entries, _ = prepare_for_csv(skill_player_stats, skill_entries, season_stats)
      elif position == quarterback:
        qb_entries, _ = prepare_for_csv(qb_stats, qb_entries, season_stats)

  validate_csv_dictionary(defense_stats)
  validate_csv_dictionary(skill_player_stats)
  validate_csv_dictionary(qb_stats)

  write_json_to_csv(defense_stats, './ProData/csvs/defensive_stats.csv')
  write_json_to_csv(skill_player_stats, './ProData/csvs/skill_player_stats.csv')
  write_json_to_csv(qb_stats, '../ProData/csvs/qb_stats.csv')
