import sys
import pandas as pd
from core import data_cleaning as dc

def show_theme():
    print("\n##############################################\n")
    print("Themes:")
    i = 1
    for theme in dc.INTERESTING_AMENITIES:
        print(f"{i}. {theme}")
        i += 1

def load_data(path):
    """
    Load data from the given path
    """
    data = pd.read_json(path, lines = True, compression = 'gzip')
    return data

def calc_score(row):
    """
    Calculate the score for the given row
    """
    score = 0
    name = row.get("name", "")
    tags = row.get("tags", {})

    if pd.isna(name) or len(name.strip()) < 5:
        score += 1

    tag_count = len(tags)
    if tag_count >= 11:
        score += 3
    elif tag_count >= 6:
        score += 2
    else:
        score += 1

    if 'wikipedia' not in tags and 'wikidata' not in tags:
        score += 1

    return score

def find_n_hidden_gems(data, n=5):
    """
    Find Top n hidden gems from the given filtered (or non-filtered) data
    
    Score is calculated based on the following criteria:
    - +1 if the name is missing or shorter than 5 characters
    - +1~3 based on the number of tags:
        - 3~5 tags → +1
        - 6~10 tags → +2
        - 11 or more tags → +3
    - +1 if both 'wikipedia' and 'wikidata' tags are missing
    
    @param data: DataFrame containing the data
    @param n: Number of hidden gems to find (default = 10)
    """

    # Apply scoring
    data['hidden_score'] = data.apply(calc_score, axis=1)

    # get Top-n
    top_n = data.sort_values(by='hidden_score', ascending=False).head(n).reset_index(drop=True)
    return top_n

def find_hidden_gems_by_type(data, amenity, n=5):
    """
    Find up to N hidden gems of a specific amenity type.

    @param data: The filtered data containing interesting places
    @param amenity: The type of amenity to filter by
    @param n: Number of top hidden places to return (default = 5)
    """
    data = find_n_hidden_gems(data, n=len(data))

    # Now filter and return top-N by amenity
    subset = dc.get_same_theme_places(data, amenity)
    if subset.empty:
        return None
    
    return subset[['name', 'amenity', 'lat', 'lon', 'hidden_score']].head(n).reset_index(drop=True)



def show_interesting_places(data, n, option, theme=None):
    filtered_places = dc.get_interesting_places(data)
    top = find_n_hidden_gems(filtered_places, n)
    
    if option == 1:
        print(f"\nTop {n} Hidden Places:\n")
        print(top[['name', 'amenity', 'lat', 'lon', 'hidden_score']])
        
    elif option == 2:
        hidden_pubs = find_hidden_gems_by_type(filtered_places, theme, n)
        if hidden_pubs is not None:
            print(f"\nTop {n} Hidden Gems for {theme}:\n")
            print(hidden_pubs[['name', 'amenity', 'lat', 'lon', 'hidden_score']])
        else:
            print(f"No places found with amenity type '{theme}'")
    

