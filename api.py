"""main file for Exist.io api parser and visualizer
Exist class used for all operations
Additional DateValues class to prevent nested dictionaries
"""



import requests
import numpy as np
import pandas as pd
#import matplotlib
#import matplotlib.pyplot as plt
#import seaborn as sns
from datetime import datetime


class Exist:
    """Exist object
    Attritbutes:
    token - Your personal token used to query Exist.io created with your
            username and password
    attributes - Your attributes - a dict of dicts
    """
    what_attributes = {"steps": 0, "steps_active_mins": 1, "floors": 2,
                       "steps_elevation": 3, "steps_distance": 4,
                       "floors_goal": 5,"steps_goal": 6, "productive_min": 7,
                       "distracting_min": 8, "commits": 9,
                       "tasks_completed": 10, "neutral_min": 11,
                       "productive_min_goal": 12, "mood": 13, "sleep": 14,
                       "time_in_bed": 16, "sleep_start": 19, "mood_note": 20,
                       "sleep_end": 21, "sleep_awakenings": 22,
                       "sleep_goal": 23, "events": 24, "weight": 25,
                       "events_duration": 26, "heartrate": 27, "tracks": 28,
                       "tweets": 29, "twitter_mentions": 30, "location": 31,
                       "location_name": 32}

    def __init__(self, token="", **kwargs):
        """Instantiation: If no username and password read token from local file
        args

        Set self.attributes["all_attributes"], self.insights, self.averages,
            self.today

        if username OR password raise both needed

        kwargs:
            username: Exist username
            password: Exist password
            all_results_limit: amount of results to return for all_results, max 31
            all_results_date_min: oldest value that can be returned YYYY-mm-dd
            all_results_date_max: newest value that can be returned YYYY-mm-dd
        """
        params = {}
        self.attributes = {"all_attributes": [], "steps": [],
                           "steps_active_min": [], "steps_distance": [],
                           "steps_goal": [], "productive_min": [],
                           "distracting_min": [], "neutral_min": [],
                           "productive_min_goal": [], "commits": [],
                           "tasks_completed": [], "mood": [], "mood_note": [],
                           "sleep": [], "time_in_bed": [], "sleep_start": [],
                           "sleep_end": [], "sleep_awakenings": [],
                           "sleep_goal": [], "events": [],
                           "events_duration": [], "weight": [],
                           "heartrate": [], "tracks": [], "location": [],
                           "checkins": [], "tweets": [],
                           "twitter_mentions": [], "location_name": []}

        self.token = token
        self.data_frames = {}
        if kwargs:
            for key in kwargs.keys():
                if key == "username":
                    params["username"] = kwargs[key]
                elif key == "password":
                    params["password"] = kwargs[key]
                elif key == "all_results_limit":
                    params["limit"] = kwargs[key]
                elif key == "all_results_date_min":
                    params["date_min"] = kwargs[key]
                elif key == "all_results_date_max":
                    params["date_max"] = kwargs[key]
                else:
                    raise ValueError("Bad keyword argument")
            if "username" in params.keys() and "password" in params.keys():
                self.get_token(params["username"], params["password"])
                params.pop("username")
                params.pop("password")
                self.get_attributes(**params)
                self.get_insights()
                self.get_averages()
                self.get_today()
            elif "username" in params.keys() or "password" in params.keys():
                raise ValueError("""Instantiation of Exist object with
                    username or password but not both.
                    Both username and password are needed to
                    Instantiate Exist with token.
                    Call get_token method to fix""")
            else:
                with open("token.txt", "r") as file:
                    self.token = file.readline().rstrip()
                self.get_attributes(**params)
                self.get_insights()
                self.get_averages()
                self.get_today()
        else:
            with open("token.txt", "r") as file:
                self.token = file.readline().rstrip()
            self.get_attributes()
            self.get_insights()
            self.get_averages()
            self.get_today()

    def get_token(self, username, password):
        """get_token("username", "password")
        Pass in username and password and set self.token to the token that
            comes back.
        Needed for exist api token

        args:
             username: Exist.io username
             password: Exist.io password

        """
        r = requests.post("https://exist.io/api/1/auth/simple-token/",
                          data={'username': username, 'password': password},
                          timeout=5)
        r.raise_for_status()
        json = r.json()
        self.token = json["token"]

    def get_today(self):
        """return requests object of today"""
        headers = {'Authorization': 'Token ' + self.token}
        r = requests.get("https://exist.io/api/1/users/$self/today/",
                         headers=headers, timeout=5)
        r.raise_for_status()
        self.today = r.json()

    def get_attributes(self, **kwargs):
        """
        set Exist.attributes to the json returned from exist api

        Kwargs:
        limit: amount of day results, max 31
        Notworking#attributes: list of attributes you want
        date_min: date in YYYY-mm-dd where to start
        date_max: date in YYYY-mm-dd where to end
        """
        params = {}
        for key in kwargs.keys():
            if key == "limit":
                if kwargs[key] > 0 and kwargs[key] <= 31:
                    params["limit"] = kwargs[key]
                else:
                    raise KeyError("Limit has to be between 1 and 31")
            #elif key == "attributes":
                #params["attributes"] = kwargs[key]
            elif key == "date_min":
                # params["date_min"] = kwargs[key]
                raise KeyError("""Date_min doesn't work, use a combination of
                max and limit""")
            elif key == "date_max":
                params["date_max"] = kwargs[key]
            else:
                raise KeyError("Bad kwarg.")
        if self.token:
            headers = {'Authorization': 'Token ' + self.token}
        else:
            raise ValueError("No token attribute, set with get_token")
        r = requests.get("https://exist.io/api/1/users/$self/attributes/",
                         headers=headers, params=params, timeout=5)
        r.raise_for_status()
        full_date = "{}-{}".format(r.json()[0]["values"][-1]["date"],
                                   r.json()[0]["values"][0]["date"])
        date_attributes = DateValues(full_date, r.json())
        self.attributes["all_attributes"].append(date_attributes)

    def get_specific_attribute(self, attribute, *kwargs):
        """(attribute, token, optional kwargs) - sets specific exist attribute

        set Exist specific attribute to the json returned from exist api

        limit: amount of day results, max 100
        page: page index, default is 1
        date_min: date in YYYY-mm-dd where to start
        date_max: date in YYYY-mm-dd where to end
        """
        params = {}
        if kwargs:
            for key in kwargs.keys():
                if key == "limit":
                    if kwargs[key] > 0 or kwargs[key] <= 31:
                        params["limit"] = kwargs[key]
                    else:
                        raise KeyError("Limit has to be between 1 and 31")
                elif key == "page":
                    params["page"] = kwargs[key]
                elif key == "date_min":
                    params["date_min"] = kwargs[key]
                elif key == "date_max":
                    params["date_max"] = kwargs[key]
                else:
                    raise KeyError("Bad kwarg.")
        if self.token:
            headers = {'Authorization': 'Token ' + self.token}
        else:
            raise ValueError("No token attribute, set with get_token")
        r = requests.get("https://exist.io/api/1/users/$self/attributes/" + attribute + "/",
                         headers=headers, params=params, timeout=5)
        r.raise_for_status()
        full_date = "{}-{}".format(r.json()["results"][-1]["date"],
                                   r.json()["results"][0]["date"])
        date_attributes = DateValues(full_date, r.json())
        self.attributes[attribute].append(date_attributes)

    def get_insights(self):
        """returns requests object of insights"""
        headers = {'Authorization': 'Token ' + self.token}
        r = requests.get("https://exist.io/api/1/users/$self/insights/",
                         headers=headers, timeout=5)
        r.raise_for_status()
        self.insights = r.json()

    def get_averages(self):
        """returns requests object of averages"""
        headers = {'Authorization': 'Token ' + self.token}
        r = requests.get("https://exist.io/api/1/users/$self/averages/",
                         headers=headers, timeout=5)
        r.raise_for_status()
        self.averages = r.json()

    def by_day(self, attribute):
        #TODO - fix this
        if self.attributes[attribute]:
            for timedelta in self.attributes[attribute]:
                thing_list = [day["value"] for day in self.attributes[attribute][timedelta].values["results"]][::-1]
                dates = [day["date"] for day in self.attributes[attribute][timedelta].values["results"]][::-1]
                what = np.array(thing_list)
                values_dates = DateValues(timedelta, what, days=[datetime.strptime(d, "%Y-%M-%d") for d in dates])
        elif self.attributes["all_attributes"]:
            for index, datevalue in enumerate(self.attributes["all_attributes"]):
                thing_list = [day["value"] for day in self.attributes["all_attributes"][index].values[self.what_attributes[attribute]]["values"][::-1]]
                dates = [day["date"] for day in self.attributes["all_attributes"][index].values[self.what_attributes[attribute]]["values"][::-1]]
                what = np.array(thing_list)
                values_dates = DateValues(datevalue.name, what, days=[datetime.strptime(d, "%Y-%M-%d") for d in dates])
        else:
            raise KeyError("Bad key")

        return values_dates

    def all_attributes_by_day(self):
        """Requires self.databutes["all_attributes"] to have been set by
        self.get_attributes()
        Sets self.data_frames[daterange] to the corresponding dataframe
        from make_dataframe"""
        all = {}
        for index, timedelta in enumerate(self.attributes["all_attributes"]):
            all[timedelta.name] = {}
            for attribute in self.attributes["all_attributes"][index].values:
                thing_list = [day["value"] for day in attribute["values"][::-1]]
                dates = [day["date"] for day in attribute["values"][::-1]]
                what = np.array(thing_list)
                values_dates = DateValues(timedelta.name, what, days=[datetime.strptime(d, "%Y-%m-%d") for d in dates])
                all[timedelta.name][attribute["attribute"]] = values_dates
            self.data_frames[timedelta.name] = self.make_dataframe(all)

    def make_dataframe(self, dict):
        """Make a pandas data-frame with the dates as indices
        Extracts inner dictionary values from DateValues object and uses them
        to create a data-frame of all Exist data with indices as dates.
        args:
            dict - nested dictionary of DateValues objects with first
            key the date range and each inner key the corresponding attribute
            and its value the corresponding DateValues object"""
        dict = list(dict.values())[0]
        dataframe_dict = {}
        dates = {}
        dates.update({"dates": dict["steps"].days})
        for key in dict:
            dataframe_dict.update({key: dict[key].values})
        dataframe = pd.DataFrame(data=dataframe_dict, index=dates["dates"])
        return dataframe

    def plot_by_day(self, attribute):
        values, days = self.by_day(attribute)

        y = list(values.values())[0]
        xs = matplotlib.dates.date2num(days)


class DateValues:
    """Helper class that has name, values and dates attributes"""
    def __init__(self, name, values, **kwargs):
        """DateValues(name, values, (days=dates))
        args:
            name: set name
            values: set values
        kwargs:
            days: set days, optional"""
        self.name = name
        self.values = values
        self.days = None
        if kwargs:
            for key in kwargs:
                if key == "days":
                    self.days = kwargs[key]

    def __str__(self):
        if self.days:
            return "DateValues| " + str(("Name: " + str(self.name), self.values,
                                                    self.days))
        else:
            return "DateValues| " + str(("Name:" + str(self.name), self.values))

    def __repr__(self):
        if self.days:
            return "DateValues| " + str(("Name: " + str(self.name), self.values,
                                                   self.days))
        else:
            return "DateValues| " + str(("Name: " + str(self.name), self.values))
