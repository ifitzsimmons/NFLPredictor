from dict_merge import merge
from position.all_positions import AllPositions

TABLE_IDENTIFIER = {'id': 'defense'}
ADVANCED_METRICS_ID = {'id': 'detailed_defense'}

class Defense(AllPositions):
  def __init__(self, player_soup):
    super().__init__(player_soup)
    self.ignore_stats = ['pos', 'uniform_number', 'av']

  def _get_advanced_metrics(self):
    advanced_metrics = {}
    adv_met_seasons = self.get_season_rows_from_table(ADVANCED_METRICS_ID)

    for season_row in adv_met_seasons:
      year, data = self.parse_row(season_row, self.ignore_stats)
      advanced_metrics[year] = data

    return advanced_metrics

  def get_career_positional_statistics(self):
    '''Combines defensive statistics and advanced metrics for defensive players'''
    seasonal_statistics = {}
    seasons = self.get_season_rows_from_table(TABLE_IDENTIFIER)

    for season_row in seasons:
      year, season_data = self.parse_row(season_row, blacklist_stats=self.ignore_stats)
      seasonal_statistics[year] = season_data

    try:
      advanced_metrics = self._get_advanced_metrics()
    except:
      advanced_metrics = {}

    return merge(seasonal_statistics, advanced_metrics)

  def get_snap_counts(self):
    columns = ['year_id', 'defense', 'def_pct']
    return self._get_snap_count_data(columns_to_include=columns)