from position.all_positions import DATA_STAT, SNAP_COUNT_IDENTIFIER, AllPositions

class Offense(AllPositions):
  def __init__(self, player_soup):
    super().__init__(player_soup)

  def get_career_positional_statistics(self):
    pass

  def get_snap_counts(self):
    columns = ['year_id', 'offense', 'off_pct']
    return self._get_snap_count_data(columns_to_include=columns)