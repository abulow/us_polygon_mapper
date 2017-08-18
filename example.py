import us_polygon_mapper.us_polygon_mapper as uspm
import pandas as pd

csv_path = "2016_election_results.csv"

print("Mapping...")

# *** Note: png creation requires PhantomJS ***

# csv_to_png()


uspm.csv_to_png(
    csv_path, "blue", "red", 0, ['state', 'trump-clinton'],
    'example.png', 'example.html')


# dict_to_html()

'''
values_dict = uspm.csv_to_values_dict(csv_path)
uspm.dict_to_html(values_dict, "purple", "brown", "median")
'''

# df_to_png()

'''
df = pd.DataFrame.from_csv(csv_path)
uspm.df_to_png(df, "green", "yellow", "percentile=90", [0, 1], "image", "web")
'''

print("Done!")