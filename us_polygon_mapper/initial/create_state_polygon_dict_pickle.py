from bs4 import BeautifulSoup
import pickle

state_polygon_dict = {}
file = BeautifulSoup(open("states.xml", "r"), "lxml")
for state in file.findAll("state"):
    state_polygon_dict[state["abbreviation"]] = {'lats': [], 'lngs': []}
    for point in state.findAll("point"):
        state_polygon_dict[state["abbreviation"]
            ]['lats'].append(float(point["lat"]))
        state_polygon_dict[state["abbreviation"]
            ]['lngs'].append(float(point["lng"]))

with open('state_polygon_dict.pickle', 'wb') as handle:
    pickle.dump(state_polygon_dict, handle, protocol=2)