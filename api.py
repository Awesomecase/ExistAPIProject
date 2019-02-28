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
        self.actual_attributes = ["steps", "steps_active_min", "steps_elevation", "steps_distance", "steps_goal", "productive_min", "distracting_min", "commits", "tasks_completed", "emails_received", "emails_sent", "neutral_min", "mood", "sleep", "workouts", "workouts_min", "sleep_start", "mood_note", "sleep_end", "events", "weight", "body_fat", "events_duration", "meditation_min", "heartrate", "tracks", "articles_read", "article_words", "tweets", "twitter_mentions", "location", "location_name", "weather_temp_max", "weather_temp_min", "weather_precipitation", "weather_air_pressure", "weather_cloud_cover", "weather_humidity", "weather_wind_speed", "day_length"]
        params = {}
        self.attributes = {"all_attributes": []}
        self.dataframe_dict = {}

        self.token = token
        self.data_frames = {}
        self.attribute_dict = {}
        self.dates = []
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
                self.prepare_attributes()
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
                self.prepare_attributes()
                self.get_insights()
                self.get_averages()
                self.get_today()
        else:
            with open("token.txt", "r") as file:
                self.token = file.readline().rstrip()
            self.get_attributes()
            self.prepare_attributes()
            self.get_insights()
            self.get_averages()
            self.get_today()

    def prepare_attributes(self):
        self.create_attribute_dict()
        self.populate_attributes_dict()
        self.reverse_attributes()
        
    def prepare_for_pandas(self):
        self.create_date_array()
        self.create_dataframe_dict()
        
    def create_dataframe_dict(self):
        for key,value in self.attributes.items():
            data_array = []
            if key in self.actual_attributes:
                for x in value.values["values"]:
                    data_array.append(x["value"])
                    self.dataframe_dict[key] = data_array

    def create_dataframe(self):
       df = pd.DataFrame(self.dataframe_dict, columns = [key for key in self.dataframe_dict.keys()]) 
       df.index = self.dates
       return df

    def reverse_attributes(self):
        for key, value in self.attributes.items():
            if key != "all_attributes":
                value.values["values"] = value.values["values"][::-1]

    def create_date_array(self):
        for x in self.attributes["mood"].values["values"]:
            self.dates.append(x["date"])

    def create_attribute_dict(self):
        count = 0
        for x in self.attributes["all_attributes"][0].values:
            self.attribute_dict.update({x["attribute"]: count})
            count = count + 1

    def populate_attributes_dict(self):
        for key, value in self.attribute_dict.items():
            for x in self.attributes["all_attributes"]:
                self.attributes.update({key: DateValues(x.name,x.values[self.attribute_dict[key]])})


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
