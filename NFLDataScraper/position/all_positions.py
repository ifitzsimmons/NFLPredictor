import re

DATA_STAT = 'data-stat'
SNAP_COUNT_IDENTIFIER = {'id': 'snap_counts'}
COMBINE_TABLE_IDENTIFIER = {'id': 'combine'}

class AllPositions:
  def __init__(self, player_soup):
    self.player_soup = player_soup

  def get_season_rows_from_table(self, table_identifier):
    '''Returns rows from table body for the given table Id on the player's page'''
    table_container = self.player_soup.find('table', table_identifier)
    table_body = table_container.find('tbody')
    return table_body.find_all('tr')

  def _get_snap_count_data(self, columns_to_include):
    '''Gets career snap count data for a player

    >>> get_snap_count_data(['year_id', 'offense', 'off_pct'])
    {'2020': {'snaps_played': 9, 'snap_played_percentage': 0.9, 'total_snaps': 10}}

    >>> get_snap_count_data(['year_id', 'defense', 'def_pct'])
    {'2020': {'snaps_played': 9, 'snap_played_percentage': 0.9, 'total_snaps': 10}}
    '''
    season_snap_counts = self.get_season_rows_from_table(SNAP_COUNT_IDENTIFIER)
    snap_count_dict = {}

    for snap_count_row in season_snap_counts:
      year = None
      snap_percent_str = None
      snaps_played = 0
      season_total_snaps = 0
      snap_percentage_float = 0

      for column in snap_count_row:
        data_stat = column.attrs[DATA_STAT]
        if data_stat not in columns_to_include:
          continue
        elif data_stat == 'year_id':
          try:
            year = column.attrs['csk']
          except:
            year = column.text
        elif data_stat in ['offense', 'defense']:
          snaps_played = int(column.text)
        elif data_stat in ['def_pct', 'off_pct']:
          snap_percent_str = column.text
        else:
          raise Exception('invalid column passed to snap count fxn')

      if year == '*' or '*+':
        continue

      if snaps_played > 0:
        snap_percent_int = re.match('\d+', snap_percent_str)[0]
        snap_percentage_float = int(snap_percent_int) / 100.0
        try:
          season_total_snaps = round(snaps_played / snap_percentage_float)
        except ZeroDivisionError:
          continue

      year = self.standardize_year(year)
      snap_count_dict[year] = {
        'snaps_played': snaps_played,
        'total_snaps': season_total_snaps,
        'snap_played_percentage': snap_percentage_float
      }

    return snap_count_dict

  def standardize_year(self, year_str):
    year_match = re.search('\d{4}', year_str)
    return year_match[0]

  def parse_row(self, row, blacklist_stats=[]):
    year = None
    stats = {}
    for column in row:
      data_stat = column.attrs[DATA_STAT]

      if data_stat in blacklist_stats:
        continue
      elif data_stat == 'year_id':
        year = column.text
        continue

      stats[data_stat] = column.text

    # PFR uses * to split up season in which player was traded
    # however, the first row for the season is the player's entire data
    # ex: https://www.pro-football-reference.com/players/C/CoopAm00.htm
    # https://www.pro-football-reference.com/players/P/PeteMa00.htm
    if year in ['*', '*+']:
      return None, None
    elif year:
      year = self.standardize_year(year)

    return year, stats

  def get_combine_data(self):
    combine_data = self.get_season_rows_from_table(COMBINE_TABLE_IDENTIFIER)
    ignore_cols = ['pos', 'year_id']

    _, stats = self.parse_row(combine_data[0], ignore_cols)
    return stats

  def get_career_positional_statistics(self):
    raise Exception('Method not implemented in base class')

  def get_snap_counts(self):
    raise Exception('Method not implemented in base class')
