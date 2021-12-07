from dict_merge import merge
from position.offense import Offense
from position.skill_player import SkillPlayer

TABLE_IDENTIFIER = {'id': 'passing'}

class Quarterback(Offense):
  def __init__(self, player_soup):
    super().__init__(player_soup)

  def get_career_positional_statistics(self):
    blacklist_stats = [
      'pos', 'uniform_number', 'av', 'QBrec'
    ]
    seasonal_statistics = {}
    seasons = self.get_season_rows_from_table(TABLE_IDENTIFIER)

    for season_row in seasons:
      year, season_data = self.parse_row(season_row, blacklist_stats=blacklist_stats)

      seasonal_statistics[year] = season_data

    skill_player = SkillPlayer(self.player_soup)
    skill_stats = skill_player.get_career_positional_statistics()

    total_stats = merge(seasonal_statistics, skill_stats)

    return total_stats