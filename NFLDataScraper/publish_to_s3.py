import json
import os
import s3fs

PROJECT_BUCKET = os.environ.get('CAPSTONE_BUCKET')

fs = s3fs.S3FileSystem(anon=False, profile='default')

def get_general_data(player_data, draft_year):
  return {
    'position': player_data['position'],
    'player_name': player_data['player_name'],
    'pro_link': player_data['pro_data_link'],
    'draft_year': draft_year
  }

def get_draft_data(player_data, draft_year):
  data = player_data['draft_data']
  data['draft_year'] = draft_year

def get_combine_data(player_data, _):
  return player_data['combine_data']

def get_career_awards(player_data, _):
  return player_data['career_awards']

def get_career_stats(player_data, _):
  return player_data['career_statistics']

def build_s3_path(position, draft_year, last_initial, player_id):
  return f'{PROJECT_BUCKET}/{position}/draft_{draft_year}/{last_initial}/{player_id}'

player_files = {
  'general.json': get_general_data,
  'draft.json': get_draft_data,
  'career_awards.json': get_career_awards,
  'combine.json': get_combine_data,
  'career_statistics.json': get_career_stats
}

if __name__ == '__main__':
  for root, _, files in os.walk('./results'):
    for file in files:
      with open(f'{root}/{file}', 'r') as player_data_file:
        players_data = json.load(player_data_file)
      year, last_initial = file.strip('.json').split('_')

      for player_id, player_data in players_data.items():
        player_position = player_data['position']

        s3_path = build_s3_path(player_position, year, last_initial, player_id)

        for s3_file, data_fxn in player_files.items():
          data = data_fxn(player_data, year)

          if not data:
            continue

          with fs.open(f'{s3_path}/{s3_file}', 'w') as s3_outfile:
            json.dump(data, s3_outfile)


