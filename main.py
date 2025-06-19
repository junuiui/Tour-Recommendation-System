# _summary_: This is the main file of the project. It contains the main function that runs the project.

# imports
import sys
import pandas as pd
from core import data_cleaning as dc
from core import tour_route_optimizer as tro
from core import interesting_place as ip
from core import find_place as fp
from core import photos_to_gpx as pg
from core import food_area as fa

def get_valid_input(input_value, min_option, max_option):
    try:
        option = int(input_value.strip())
        if (option < min_option or option > max_option):
            raise ValueError
        return option
    except ValueError:
        print("Invalid option. Please try again.")
        return -1

def get_valid_type(input_value, all_type):
    try:
        input_type = input_value.strip().lower()
        all_type = list(all_type)
        if input_type not in all_type:
            raise ValueError
        return input_type
    except ValueError:
        print("Invalid type. Please try again.")
        return -1

def get_photo_csv_to_df():
    """
    Read the photo csv file and return the dataframe
        @return None if fail
    """
    print("Please input photos.csv file")
    input_file = input("Enter file name: ").strip()
    try:
        photos = pd.read_csv(input_file)
        photos = dc.photo_clean_data(photos)
        return photos
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
        return None

def find_nearest_walking_path(start_point, places_df):
    remaining = places_df.copy().reset_index(drop=True)
    path = []
    current = start_point

    while not remaining.empty:
        distances = []
        for i, row in remaining.iterrows():
            dist, success = tro.walking_route_distance(current[0], current[1], row['lat'], row['lon'])
            if success:
                distances.append((i, dist))
        
        if not distances:
            break 

        nearest_idx, nearest_dist = min(distances, key=lambda x: x[1])
        nearest_place = remaining.iloc[nearest_idx]
        path.append(nearest_place)
        current = (nearest_place['lat'], nearest_place['lon'])
        remaining = remaining.drop(remaining.index[nearest_idx]).reset_index(drop=True)

    return path

def main():

    # read data
    file = sys.argv[1]
    data = dc.basic_clean_data(pd.read_json(file, lines=True, compression='gzip'))
     
    # load OSM
    print("Loading OSM data... (this may take a while)")
    tro.load_graph()

    print("Ready to explore? Choose an option below!")

    while (True):
        # Option starts
        # TODO: we can add more options here
        print("\n============================================================\n")
        print(" Options:")
        print("     0. Exit")
        print("     1. Find hidden gems")
        print("     2. Find hidden gems by theme")
        print("     3. Find near anities by photos")
        print("     4. Find near food place by photos")
        print("     5. Use photos create gpx file")
        print("     6. Tour route recommendation (straight line distance)")
        print("     7. Walking tour route recommendation (Only Metro Vancouver)")
        print("     8. Driving tour route recommendation (Only Metro Vancouver)")
        print("     9. Get the map for all food place in Vancouver")
        print("     10. Show unique type that in tha data")
        print("     11. Get the map for a type in Vancouver")
        print("\n============================================================\n")

        # get input
        option = input("Enter the option number: ")
        option = get_valid_input(option, 0, 11)

        if option == 0:
            print("Exiting...")
            break
        
        elif option == 1:
            print("How many hidden gems do you want to find?")
            input_val = input("Enter the number of hidden gems(1 to 10): ")
            input_val = get_valid_input(input_val, 1, 10)  # here,
            if not input_val == -1:
                ip.show_interesting_places(data, input_val, 1)
            else:
                continue

        elif option == 2:
            while (True):
                print("What theme do you want to find hidden gems for? (type list if want to see the list of themes)")
                input_val = input("Enter the theme: ").strip().lower()
                if (input_val == "list"):
                    ip.show_theme()
                    continue
                
                print("How many hidden gems do you want to find?")
                input_val2 = input("Enter the number of hidden gems(1 to 10): ")
                input_val2 = get_valid_input(input_val2, 1, 10)
                if not input_val2 == -1:
                    ip.show_interesting_places(data, input_val2, 2, input_val)
                    break
                else:
                    break

        elif option == 3:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            while (True):
                print("\nAvaiable photos:")
                print("    0. Exit")
                for idx, row in photos.iterrows():
                    print(
                        f"    {idx+1}. {row['timestamp']} (Lat: {row['latitude']}, Lon: {row['longitude']})")
                photo_idx = input("Select a photos number: ")
                photo_idx = get_valid_input(photo_idx, 0, len(photos))
                if (photo_idx == 0):
                    print("Back to main")
                    break
                elif (photo_idx > 0):
                    near_places = fp.find_near_amenities(photos.iloc[photo_idx - 1], data)
                    near_places_save = pd.DataFrame([{
                        'Name': place['name'], 'Amenity': place['amenity'], 'Distance(km)': f'{distance:.2f}'
                    } for place, distance in near_places])

                    near_places_save.to_csv(f"nearby_anities_photo-{photo_idx}.csv", index = False)
                    
                    print(f"\nNearby places within 1 km:")
                    for i, (place, distance) in enumerate(near_places, 1):
                        print(
                            f"{i}. Name: {place['name']}, Amenity: {place['amenity']}, Distance: {distance:.2f} km")
                    
                    print(f'\nNearby places saved to nearby_anities_photo-{photo_idx}.csv')
                elif (photo_idx == -1):
                    continue

        elif option == 4:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            while (True):
                print("\nAvaiable photos:")
                print("    0. Exit")
                for idx, row in photos.iterrows():
                    print(
                        f"    {idx+1}. {row['timestamp']} (Lat: {row['latitude']}, Lon: {row['longitude']})")
                photo_idx = input("Select a photos number: ")
                photo_idx = get_valid_input(photo_idx, 0, len(photos))
                if (photo_idx == 0):
                    print("Back to main")
                    break
                max_distance_km = input("How far you want to find(1 to 3 km): ")
                max_distance_km = get_valid_input(max_distance_km, 1, 3)
                if(max_distance_km == -1):
                    continue
                if (photo_idx > 0):
                    near_food = fp.find_near_food(photos.iloc[photo_idx - 1], data, max_distance_km)

                    near_food_save = pd.DataFrame([{
                        'Name': place['name'], 'Amenity': place['amenity'], 'Distance(km)': f'{distance:.2f}'
                    } for place, distance in near_food])

                    near_food_save.to_csv(f"nearby_food_photo-{photo_idx}.csv", index = False)

                    print(f'\nNearby places within {max_distance_km:.2f} km:')
                    for i, (place, distance) in enumerate(near_food, 1):
                        print(
                            f"{i}. Name: {place['name']}, Amenity: {place['amenity']}, Distance: {distance:.2f} km")

                    print(f'\nNearby places saved to nearby_food_photo-{photo_idx}.csv')
                elif (photo_idx == -1):
                    continue

        elif option == 5:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            photos['timestamp'] = pd.to_datetime(photos['timestamp'])
            gpx_file = pg.photos_to_gpx(photos)

            with open('photos.gpx', 'w') as f:
                f.write(gpx_file.to_xml())

            print(f"photos.gpx is create in file")
            print("\n")
        
        elif option == 6:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            print("\nAvailable photos:")
            for idx, row in photos.iterrows():
                print(f"    {idx+1}. {row['timestamp']} (Lat: {row['latitude']}, Lon: {row['longitude']})")
            photo_idx = input("Select a photo number to start tour from: ")
            photo_idx = get_valid_input(photo_idx, 1, len(photos))
            if photo_idx == -1:
                continue
            
            start_point = (photos.iloc[photo_idx - 1]['latitude'], photos.iloc[photo_idx - 1]['longitude'])

            print("How many places do you want in the tour route?")
            num = input("Enter number(2 to 10): ")
            num = get_valid_input(num, 2, 10)
            if num == -1:
                continue

            filtered_places = dc.get_interesting_places(data)
            hidden_places = ip.find_n_hidden_gems(filtered_places, n=(num*3))

            # No dup themes!
            unique_theme_places = tro.remove_duplicate_amenities(hidden_places).head(num)
            route = tro.find_nearest_path(start_point, unique_theme_places)
            
            current = start_point
            total_dist = 0.0
            # Note that the distance is straight line distance, not the actual walking distance
            print("\nRecommended Tour Path:")
            
            for i, place in enumerate(route, 1):
                dist = tro.haversine(current[0], current[1], place['lat'], place['lon'])
                start_dist = tro.haversine(start_point[0], start_point[1], place['lat'], place['lon'])
                total_dist += dist
                print(f"{i}. {place['name']} ({place['amenity']}) +{dist:.2f} km (from start: {start_dist:.2f} km)")
                current = (place['lat'], place['lon'])
            print(f"\nTotal Distance: {total_dist:.2f} km\n\n")
            
        elif option == 7:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            def find_nearest_walking_path(start_point, places_df):
                remaining = places_df.copy().reset_index(drop=True)
                path = []
                current = start_point

                while not remaining.empty:
                    distances = []
                    for i, row in remaining.iterrows():
                        dist, _ = tro.walking_route_distance(current[0], current[1], row['lat'], row['lon'])
                        if dist is not None:
                            distances.append((i, dist))
                    
                    if not distances:
                        break

                    nearest_idx, nearest_dist = min(distances, key=lambda x: x[1])
                    nearest_place = remaining.iloc[nearest_idx]
                    path.append(nearest_place)
                    current = (nearest_place['lat'], nearest_place['lon'])
                    remaining = remaining.drop(index=nearest_idx).reset_index(drop=True)

                return path

            print("\nAvailable photos:")
            for idx, row in photos.iterrows():
                print(f"    {idx+1}. {row['timestamp']} (Lat: {row['latitude']}, Lon: {row['longitude']})")
            photo_idx = input("Select a photo number to start tour from: ")
            photo_idx = get_valid_input(photo_idx, 1, len(photos))
            if photo_idx == -1:
                continue

            start_point = (photos.iloc[photo_idx - 1]['latitude'], photos.iloc[photo_idx - 1]['longitude'])

            print("How many places do you want in the walking tour route?")
            num = input("Enter number(2 to 10): ")
            num = get_valid_input(num, 2, 10)
            if num == -1:
                continue

            filtered_places = dc.get_interesting_places(data)
            hidden_places = ip.find_n_hidden_gems(filtered_places, n=(num * 3))
            unique_theme_places = tro.remove_duplicate_amenities(hidden_places).head(num)

            route = find_nearest_walking_path(start_point, unique_theme_places)

            current = start_point
            total_dist = 0.0
            cumulative_dist = 0.0 

            print("\nRecommended Walking Tour Path:")
            for i, place in enumerate(route, 1):
                dist, _ = tro.walking_route_distance(current[0], current[1], place['lat'], place['lon'])
                cumulative_dist += dist
                total_dist += dist
                print(f"{i}. {place['name']} ({place['amenity']}) +{dist:.2f} km (from start: {cumulative_dist:.2f} km)")
                current = (place['lat'], place['lon'])

            print(f"\nTotal Walking Distance: {total_dist:.2f} km\n")
            
        elif option == 8:
            photos = get_photo_csv_to_df()
            if photos is None:
                continue
            
            def find_nearest_driving_path(start_point, places_df):
                remaining = places_df.copy().reset_index(drop=True)
                path = []
                current = start_point

                while not remaining.empty:
                    distances = []
                    for i, row in remaining.iterrows():
                        dist, _ = tro.driving_route_distance(current[0], current[1], row['lat'], row['lon'])
                        if dist is not None:
                            distances.append((i, dist))

                    if not distances:
                        break

                    nearest_idx, nearest_dist = min(distances, key=lambda x: x[1])
                    nearest_place = remaining.iloc[nearest_idx]
                    path.append(nearest_place)
                    current = (nearest_place['lat'], nearest_place['lon'])
                    remaining = remaining.drop(index=nearest_idx).reset_index(drop=True)

                return path

            print("\nAvailable photos:")
            for idx, row in photos.iterrows():
                print(f"    {idx+1}. {row['timestamp']} (Lat: {row['latitude']}, Lon: {row['longitude']})")
            photo_idx = input("Select a photo number to start tour from: ")
            photo_idx = get_valid_input(photo_idx, 1, len(photos))
            if photo_idx == -1:
                continue

            start_point = (photos.iloc[photo_idx - 1]['latitude'], photos.iloc[photo_idx - 1]['longitude'])

            print("How many places do you want in the driving tour route?")
            num = input("Enter number(2 to 10): ")
            num = get_valid_input(num, 2, 10)
            if num == -1:
                continue

            filtered_places = dc.get_interesting_places(data)
            hidden_places = ip.find_n_hidden_gems(filtered_places, n=(num * 3))
            unique_theme_places = tro.remove_duplicate_amenities(hidden_places).head(num)

            route = find_nearest_driving_path(start_point, unique_theme_places)

            current = start_point
            total_dist = 0.0
            cumulative_dist = 0.0

            print("\nRecommended Driving Tour Path:")
            for i, place in enumerate(route, 1):
                dist, _ = tro.driving_route_distance(current[0], current[1], place['lat'], place['lon'])
                cumulative_dist += dist
                total_dist += dist
                print(f"{i}. {place['name']} ({place['amenity']}) +{dist:.2f} km (from start: {cumulative_dist:.2f} km)")
                current = (place['lat'], place['lon'])

            print(f"\nTotal Driving Distance: {total_dist:.2f} km\n")

        elif option == 9:
            m = fa.create_food_map(data)
            m.save('food_amenities_map.html')
            print("food_amenities_map.html is create in file")

        elif option == 10:
            unique = fp.show_all_amenity_type(data)
            unique.to_csv('unique.csv', index = False)
            print("unique.csv is create in file")
        
        elif option == 11:
            while(True):
                print("0. Exit")
                print("1. Get the type map")
                option = input("Enter the option number: ")
                option = get_valid_input(option, 0, 1)
                if option == 0:
                    print("Back to main")
                    break
                elif option == 1:
                    amenity_type = input("Enter the type you want to find(from list of option 10): ")
                    unique = fp.show_all_amenity_type(data)
                    amenity_type = get_valid_type(amenity_type, unique)
                    if amenity_type == -1:
                        continue
                    m = fp.make_map(data,amenity_type)
                    m.save(f'{amenity_type}_map.html')
                    print(f"{amenity_type}_map.html is create in file")
                elif option == -1:
                    continue
                



if __name__ == '__main__':
    main()


