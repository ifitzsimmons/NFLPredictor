from pprint import pprint

def merge(a, b, path=None):
  '''merges b into a

  >>> merge({'2020': {'stat1': 1, 'stat2': 2}, '2019': {'stat3': 3}}, {'2020': {'stat5': 5}, '2019': {'stat6': 6}})
  {'2020': {'stat1': 1, 'stat2': 2, 'stat5': 5}, '2019': {'stat3': 3, 'stat6': 6}}

  >>> merge({'2020': {'stat1': 1, 'stat2': 2}, '2019': {'stat3': 3}}, {'2020': {'stat1': 1, 'stat5': 5}, '2019': {'stat6': 6}})
  {'2020': {'stat1': 1, 'stat2': 2, 'stat5': 5}, '2019': {'stat3': 3, 'stat6': 6}}

  >>> merge({'2020': {'stat1': 1, 'stat2': 2}, '2019': {'stat3': 3}}, {'2020': {'stat1': 2, 'stat5': 5}, '2019': {'stat6': 6}})
  Traceback (most recent call last):
  ...
  Exception: Conflict at 2020.stat1

  '''
  if path is None: path = []
  for key in b:
    if key in a:
      if isinstance(a[key], dict) and isinstance(b[key], dict):
        merge(a[key], b[key], path + [str(key)])
      elif a[key] == b[key]:
        pass # same leaf value
      elif not a[key] or not b[key]:
        a[key] = a[key] or b[key]
      else:
        a[key] = b[key]
        print('Conflict at %s' % '.'.join(path + [str(key)]))
    else:
      a[key] = b[key]
  return a