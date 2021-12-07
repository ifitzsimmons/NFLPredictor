from position.offense import Offense

RUSHING_IDENTIFIER = {'id': 'rushing_and_receiving'}
RECEIVING_IDENTIFIER = {'id': 'receiving_and_rushing'}

# TE, WR, RB, FB
class SkillPlayer(Offense):
  def __init__(self, player_soup):
    super().__init__(player_soup)

  def get_career_positional_statistics(self):
    blacklist_stats = ['pos', 'uniform_number']
    seasonal_statistics = {}

    try:
      seasons = self.get_season_rows_from_table(RUSHING_IDENTIFIER)
    except AttributeError:
      seasons = self.get_season_rows_from_table(RECEIVING_IDENTIFIER)

    for season_row in seasons:
      year, season_data = self.parse_row(season_row, blacklist_stats=blacklist_stats)

      seasonal_statistics[year] = season_data

    return seasonal_statistics