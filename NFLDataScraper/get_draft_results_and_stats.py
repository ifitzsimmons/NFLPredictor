from typing import DefaultDict, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime as dt
from time import sleep

import re
import requests
from dict_merge import merge
from position.all_positions import AllPositions
from position.defense import Defense
from position.offense import Offense
from position.quarterback import Quarterback
from position.skill_player import SkillPlayer

import json

"""TODO
1. Add link ref for each player to a dictionary
2. Skip defensive/offensive processing depending on position
"""

players_with_no_page = {}

def get_draft_html_response(year: int) -> requests.Response:
  '''Returns html response for given draft year

  Args:
    year: Year of the draft

  Returns:
    Request Response for a link.
  '''
  url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'
  return requests.get(url)

def get_player_data_rows(soup: BeautifulSoup) -> List[BeautifulSoup]:
  '''Returns rows for all players drafted in the given year

  Args:
    soup: Beautiful soup for players page on Pro Football Reference

  Returns:
    All rows excluding the header row from the draft data.
  '''
  div = soup.find_all('div', {'class' : 'table_container'})[0]
  table_rows = div.find_all('tr', {'class': None})
  return table_rows[1:]

def get_player_url_extension(column: BeautifulSoup) -> str:
  '''
  Find the a tag for the player in the draft table in order to find
  the extension for the player's personal page on Pro Football Reference.

  Args:
    column: Player column from the draft data table

  Returns:
    ext_string: Extension for the player for his pro football reference page
  '''
  # Look for correct link extension
  ext_pattern = re.compile('^/players')

  a = column.find('a')
  ext_string = (a.attrs['href'])
  # Check that extension is for the player
  # by searching for the `/player` extension
  assert re.search(ext_pattern, ext_string), 'Player has no page on pro reference'

  return ext_string

def get_player_initial_and_id(url_ext: str) -> Tuple[str, str]:
  '''Returns first initial of player's last name and their unique player id

  >>> get_player_initial_and_id(/players/P/ParsMi00.htm)
  P, ParsMi00

  Args:
    url_ext: The players URL extension for pro football reference

  Raises:
    TypeError: if player extension link is invalid.
  '''
  pat = re.compile('\\/players\\/([A-Z])\\/([A-z]+[0-9]*.*)\\.htm*')
  player_info_groups = re.match(pat, url_ext)
  last_name_initial = player_info_groups[1]
  player_id = player_info_groups[2]
  return last_name_initial, player_id

def get_player_draft_data(player_info: BeautifulSoup):
  '''
  Returns data for a drafted player.

  Args:
    player_info: Row for a player in the draft table.

  Returns:
    draft_data: Dictionary with the following keys
      draft_pick (str): Overall draft pick of the player
      draft_round (str): Round the player was drafted in
      team (str): Team the player was drafted to
      player (str): Name of the player
      pos (str): Players drafted position
      age (str): Players age when drafted

    extension (str): The pro football reference page extension for the player's
      career web page.

    player_lastname_initial (str): First initial of player's last name

    player_id (str): Unique player identifier for pro football reference

    player_position (str): Position player was drafted to.

  Raises:
    TypeError: If player data is missing expected column
  '''
  draft_data_stats = ['draft_pick', 'team', 'player', 'pos', 'age']
  draft_data = {}

  draft_round = player_info.find('th', {'data-stat': 'draft_round'})
  draft_data['draft_round'] = draft_round.text

  for stat in draft_data_stats:
    data_stat = player_info.find('td', {'data-stat': stat})
    draft_data[stat] = data_stat.text

    if stat == 'player':
      try:
        extension = get_player_url_extension(data_stat)
      except AttributeError:
        return
      player_lastname_initial, player_id = get_player_initial_and_id(extension)
    elif stat == 'pos':
      player_position = data_stat.text

  return draft_data, extension, player_lastname_initial, player_id, player_position

def get_career_awards_data(player_info: BeautifulSoup) -> Dict[str, str]:
  '''
  Returns career awards for a player including the following:
    1. Number of times named to all pro first team (Best at position for year)
    2. Number of time selected for Pro Bowl (all star game)
    3. Years as the primary starter

  Args:
    player_info: Row for a player in the draft table.

  Returns:
    Dictionary of player's career awards

  Raises:
    TypeError: If expected column is missing from player row.
  '''
  career_awards = ['all_pros_first_team', 'pro_bowls', 'years_as_primary_starter']
  career_awards_data = {}

  for stat in career_awards:
    data_stat = player_info.find('td', {'data-stat': stat})

    career_awards_data[stat] = data_stat.text

  return career_awards_data

def get_player_class(player_position: str, soup: BeautifulSoup) -> Optional[AllPositions]:
  '''
  Creates player class for the player specific to the player's position.

  This player class provides player-specific methods for collecting
  player data.

  Args:
    player_position: Code for player's drafted position
    soup: Beautiful soup object for player's personal page
      on Pro Football Reference

  Returns:
    Class for handling player data parsing
  '''
  if player_position in ['K', 'LS', 'P']:
    return

  if player_position == 'QB':
    return Quarterback(soup)
  elif player_position in ['WR', 'RB', 'TE', 'FB']:
    return SkillPlayer(soup)
  elif player_position in ['T', 'C', 'OL', 'G']:
    return Offense(soup)
  else:
    return Defense(soup)

def get_player_page_data(player_extension: str, player_position: str) -> Optional[dict]:
  '''
  Returns player career statistics and combine data from Player's Pro Football
  Reference page

  Args:
    player_extension: Player's page extension for Pro Football Reference.
    player_position: Player's positional code

  Returns
    Dictionary with the following fields:
      career_statistics (dict[str, list[dict]]): Dict of list of season stats
      combine_data (dict): players combine data
      pro_data_link (str): Players pro link

  '''
  link = f'https://www.pro-football-reference.com{player_extension}'

  # Request player HTML
  sup_request = requests.get(link)
  html_text = re.sub('<!--|-->', '', sup_request.text)
  player_soup = BeautifulSoup(html_text, 'html.parser')

  player = get_player_class(player_position, player_soup)

  if not player:
    return None

  try:
    career_statistics = player.get_career_positional_statistics()
  except AttributeError:
    career_statistics = {}

  try:
    career_snap_counts = player.get_snap_counts()
  except AttributeError:
    career_snap_counts = {}

  try:
    combine_data = player.get_combine_data()
  except AttributeError:
    combine_data = {}

  return {
    'career_statistics': merge(career_statistics or {}, career_snap_counts or {}),
    'combine_data': combine_data,
    'pro_data_link': link
  }

def get_year_draft_info(year: int) -> dict:
  '''
  Get all draft information and career statistics
  per player in a given year

  Args:
    year: int
        year in which draft data exists for
        https://www.pro-football-reference.com

  Returns:
    draft_dict: dictionary with ALL player data from a given draft
  '''
  response = get_draft_html_response(year)
  soup = BeautifulSoup(response.text, 'html.parser')

  # retrieve div for draft table and then get all rows
  player_data_rows = get_player_data_rows(soup)

  draft_dict = defaultdict(dict)

  # This loop collects all the data for each player in
  # the year's draft class
  for player_info in player_data_rows:
    player_data = {}

    try:
      draft_data, extension, player_lastname_initial, player_id, player_position = get_player_draft_data(player_info)
    except TypeError:
      continue

    career_awards = get_career_awards_data(player_info)
    player_data = {
      'position': player_position,
      'player_name': draft_data['player'],
      'career_awards': career_awards,
      'draft_data': draft_data,
    }
    player_page_data = get_player_page_data(extension, player_position)

    try:
      draft_dict[player_lastname_initial][player_id] = {**player_data, **player_page_data}
    except TypeError:
      # If no player page data
      continue

  return draft_dict

if __name__ == '__main__':
  '''
  This module scrapes each draft for the last N years and gets the player data.
  It writes the raw data to the `results` folder.
  '''
  # TODO - use argparse to configure
  num_drafts = 21

  end_year = dt.now().year
  first_year = end_year - num_drafts

  draft_years = list(range(first_year, end_year))

  '''COLS IN DRAFT TABLE'''
  draft_stats = ['draft_round', 'draft_pick']
  offensive_stats = [
    'pass_att', 'pass_cmp', 'pass_int', 'pass_td', 'pass_yds',
    'rec', 'rec_td','rec_yds', 'rush_att', 'rush_td', 'rush_yds',
  ]
  cols = [
    'pos', 'all_pros_first_team', 'g', 'pro_bowls', 'years_as_primary_starter'
  ]
  defensive_stats = ['sacks', 'tackles_solo']
  '''COLS IN DRAFT TABLE END'''

  # Data that is not in original draft table
  supplemental_stats = ['seasons_played', 'gs']
  defensive_supplemental_stats = [
    'pass_defended', 'fumbles_forced', 'fumbles_rec',
    'tackles_combined', 'tackles_assists', 'tackles_loss',
    'qb_hits', 'safety_md'
  ]

  for i, year in enumerate(draft_years):
    if i > 0:
      sleep(60)

    result = get_year_draft_info(year)
    if result:
      for last_initial, player_data in result.items():
        with open(f'./ProData/results/{year}_{last_initial}.json', 'w') as outfile:
          json.dump(player_data, outfile)
