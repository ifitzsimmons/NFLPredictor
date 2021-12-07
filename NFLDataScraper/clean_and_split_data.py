import json
from pprint import pprint
import os
from typing import List

from collections import defaultdict

def write_positional_data(data, file_path):
  for position, player_data in data.items():
    with open(f'{file_path}/{position}.json', 'w') as outfile:
      json.dump(player_data, outfile)

def combine_positions(position: str) -> str:
  '''
  For analysis purposes, there are some positions that we want to group together.
  For instance Cornerbacks (CBs) and Defensive Backs (DBs) are both defensive
  backs and we want to treat them as such. Similarly, Inside Linebackers (ILBs),
  Outside Linebackers (OLBs) and Linebackers (LBs) are all just LBs.

  Args:
    position: Player position according to NFL data.

  Returns:
    position: Grouped player position when applicable

  Examples:
    >>> combine_positions('CB')
    'DB'
    >>> combine_positions('DB')
    'DB'

  '''
  if position in ['CB']:
    return 'DB'
  elif position in ['NT']:
    return 'DT'
  elif position in ['ILB', 'OLB']:
    return 'LB'
  elif position in ['C', 'G','T']:
    return 'OL'
  else:
    return position

def convert_data_to_numbers(data: dict):
  '''
  Converts numerical values wrapped as strings to ints or floats
  in a dictionary

  Args:
    data: Arbitrary dictionary with nesting level set to 1!

  Returns:
    data: Data dictionary with numeric conversions

  Raises:
    TypeError: If dictionary is nested.

  Examples:
    >>> convert_data_to_numbers({'string_f': '0.1', 'string_i': '10', 'string': 'hello', 'i': 1})
    {'string_f': 0.1, 'string_i': 10, 'string': 'hello', 'i': 1}

    >>> convert_data_to_numbers({'nested': {'si': '10'}})
    Traceback (most recent call last):
    ...
    TypeError: int() argument must be a string, a bytes-like object or a number, not 'dict'
  '''

  for stat, value in data.items():
    if not value:
      data[stat] = 0
      continue
    elif type(value) in [int, float]:
      if stat == 'total_snaps':
        data[stat] = round(value)
      continue
    elif '%' in value:
      data[stat] = float(value.replace('%', ''))

    try:
      data[stat] = int(value)
    except ValueError:
      try:
        data[stat] = float(value)
      except ValueError:
        pass
  return data

def get_game_outcomes(qb_record: str) -> List[int]:
  '''
  Converts the QB record string into wins, losses and ties (integers).

  Args:
    qb_record: Wins-ties-losses (10-3-3)

  Returns:
    wins, ties, losses: [10, 3, 3]

  Examples:
    >>> get_game_outcomes('10-3-3')
    [10, 3, 3]

    >>> get_game_outcomes(None)
    [0, 0, 0]
  '''
  if not qb_record:
    return [0, 0, 0]
  return list(map((lambda x: int(x) if x else 0), qb_record.split('-')))

def add_qb_stats(data: dict):
  '''
  Enhances quarterback player data with quarterback-specific data
    1. Adds number of wins, ties, and losses for a given season
    2. Calculates the quarterbacks win percentage

  If season does not have a qb record statistic, this function will
  return the initial data structure.

  Args:
    data: Quarterback's season data.

  Returns:
    data: Enhanced data with win information

  Examples:
    >>> add_qb_stats({'qb_rec': '5-3-2'})
    {'wins': 5, 'losses': 3, 'ties': 2, 'win_percentage': 0.5}

    >>> add_qb_stats({'qb_rec': '0-0-0'})
    {'wins': 0, 'losses': 0, 'ties': 0, 'win_percentage': None}
  '''
  try:
    record = data['qb_rec']
  except KeyError:
    return data

  wins, losses, ties = get_game_outcomes(record)

  del data['qb_rec']
  data['wins'] = int(wins) if wins else 0
  data['losses'] = int(losses) if wins else 0
  data['ties'] = int(ties) if wins else 0

  try:
    data['win_percentage'] = wins / (wins + losses + ties)
  except ZeroDivisionError:
    data['win_percentage'] = None

  return data

def clean_data(data: dict, is_quarterback=False):
  '''
  Adds quarterback-specific data if necessary and converts
  strings to numbers where appropriate

  Args:
    data: Player data for a season.
    is_quarterback (:obj:`bool`, optional): If data is quarterback data,
      default behavior is False

  Returns:
    data: cleaned data.

  Examples:
    >>> clean_data({'string_f': '0.1'})
    {'string_f': 0.1}

    >>> clean_data({'string_f': '0.1', 'qb_rec': '5-3-2'}, True)
    {'string_f': 0.1, 'wins': 5, 'losses': 3, 'ties': 2, 'win_percentage': 0.5}

    >>> clean_data({'string_f': '0.1', 'qb_rec': '5-3-2'})
    {'string_f': 0.1, 'qb_rec': '5-3-2'}
  '''

  if is_quarterback:
    add_qb_stats(data)

  return convert_data_to_numbers(data)

if __name__ == '__main__':
  '''
  This module parses the raw data from the Web scraper and splits it out into logical folders

    1. ProData/cleaned/combine
      * Stores combine data and partitions by position
    2. ProData/cleaned/draft_data
      * Stores draft data and partitions by position
    3. ProData/cleaned/awards
      * Stores career awards data and partitions by position
    4. ProData/cleaned/season_stats/{position}
      * Stores seasonal statistics data and partitions by position
  '''
  career_awards = defaultdict(dict)
  combine_data = defaultdict(dict)
  draft_data = defaultdict(dict)
  player_id_to_name_map = defaultdict(dict)
  seasonal_stats = defaultdict(defaultdict)

  for root, _, files in os.walk('./ProData/results'):
    for file in files:
      draft_year, last_initial = file.strip('.json').split('_')

      with open(f'{root}/{file}', 'r') as player_data_file:
        nfl_player_data = json.load(player_data_file)

      for player_id, all_data in nfl_player_data.items():
        position = combine_positions(all_data['position'])

        player_id_to_name_map[player_id]['name'] = all_data['player_name']
        player_id_to_name_map[player_id]['link'] = all_data['pro_data_link']
        player_id_to_name_map[player_id]['position'] = all_data['position']

        combine_data[position][player_id] = clean_data(all_data['combine_data'])
        career_awards[position][player_id] = clean_data(all_data['career_awards'])
        draft_data[position][player_id] = clean_data(all_data['draft_data'])
        draft_data[position][player_id]['year'] = draft_year

        for year, season_stats in all_data['career_statistics'].items():
          if not season_stats and year == 'null':
            # This was done to handle seasons where player was traded
            # data was split into three rows, 1 with all data, and
            # then 1 for each team.
            continue

          # age is not recorded for something like position change
          # reason provided if player suspended for season
          if 'age' not in season_stats or 'reason' in season_stats:
            continue
          season_data = clean_data(season_stats, position == 'QB')
          player_age = season_data['age']
          season_data['player_id'] = player_id

          # THIS IS A HACK, SHOULD SAVE POSITION FOR EACH SEASON THE PLAYER PLAYS
          season_data['position'] = position

          if not seasonal_stats[position] or player_age not in seasonal_stats[position]:
            seasonal_stats[position][player_age] = []

          seasonal_stats[position][player_age].append(season_data)

  write_positional_data(combine_data, './ProData/cleaned/combine')
  write_positional_data(draft_data, './ProData/cleaned/draft_data')
  write_positional_data(career_awards, './ProData/cleaned/awards')
  with open('./ProData/cleaned/player_id_info.json', 'w') as outfile:
    json.dump(player_id_to_name_map, outfile)

  for position, age_seasons in seasonal_stats.items():
    if not os.path.isdir(f'./ProData/cleaned/season_stats/{position}'):
      os.mkdir(f'./ProData/cleaned/season_stats/{position}')

    for age, season_data in age_seasons.items():
      with open(f'./ProData/cleaned/season_stats/{position}/age_{age}.json', 'w') as outfile:
        json.dump(season_data, outfile)
