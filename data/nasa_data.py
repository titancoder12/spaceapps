# import json

# with open('neows.json') as f:
#     data = json.load(f)
#     for obj in data['near_earth_objects']:
#         for date in data['near_earth_objects'][]:
#         print(f"Name: {obj['name']}, Diameter (m): {obj['estimated_diameter']['meters']['estimated_diameter_max']}, Hazardous: {obj['is_potentially_hazardous_asteroid']}")



import requests, json
from datetime import date, timedelta

def fetch_neo_feed(api_key, start_date, end_date):
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': api_key
    }
    data = requests.get(url, params=params).json()
    return data

# Example usage:
def get_asteroid(start_date=None, end_date=None, live=True):
    if start_date is None:
        start_date = date.today().strftime("%Y-%m-%d")
    if end_date is None:
        end_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    if live:
        feed_data = fetch_neo_feed('GlXGvGdXXtlWY4rPqR3O9iX8dH4uKseNmamKL1FK', start_date, end_date)
    else:
        with open('data/my_data.json') as f:
            feed_data = json.load(f)

    #print(feed_data)  # For debugging
    # Now parse the JSON to extract asteroids
    
    asteroids = []
    for date_str, ast_list in feed_data['near_earth_objects'].items():
        for ast in ast_list:
            name = ast['name']
            diameter = ast['estimated_diameter']['kilometers']['estimated_diameter_max']
            velocity = float(ast['close_approach_data'][0]['relative_velocity']['kilometers_per_hour'])
            miss_km = float(ast['close_approach_data'][0]['miss_distance']['kilometers'])
            # Use these values to create a game asteroid (scaling units as needed)
            asteroids.append(ast)
            #print(f"Date: {date_str}, Name: {name}, Diameter (km): {diameter:.3f}, Velocity (km/h): {velocity:.1f}, Miss Distance (km): {miss_km:.1f}")
    
    return asteroids

if __name__ == "__main__":
    asteroids = get_asteroid()
    print(json.dumps(asteroids[0], indent=4))
    print(f"Total asteroids found: {len(asteroids)}")