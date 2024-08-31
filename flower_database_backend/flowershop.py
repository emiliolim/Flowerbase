"""
Emilio Lim
8/7/24
Python 3.9

This is my first attempt at creating a flower shop
app from scratch
This app manages client base and provides meaningful functions that
will help manage client base and data visualization of previous sales

The program first takes a CSV of the original flower shop data, which
then is converted to an SQL data table which increases efficiency
and performance of the program to the front end of the program.

Clients will be able to query portions of the data without needing to
read all of it

For this program I will be using a test data template from Kaggle as a
base for the functions I will create

Note for future self: create unit tests for remaining functions

"""
from numpy import *
from datetime import date
from os import path

import pandas as pd
import sqlite3 as sql
from dataclasses import dataclass
import datetime as dt
import matplotlib.pyplot as plt

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}


class DataNotFound(Exception):
    def __init__(self):
        message = f"No data is found for the given parameters"
        super().__init__(message)


class ImproperDataFormat(Exception):
    def __init__(self):
        message = "Improper data format within the given parameters"
        super().__init__(message)


@dataclass
class FlowerDataBase:
    filename: str = None
    file_import: pd.DataFrame = None
    connection: sql.Connection = sql.connect(
        'flowershopdata.sqlite')

    def import_file(self):
        """
        Initializes file import into readable format for Python
        ***MUST*** include .csv or .sql extension
        """
        try:
            if path.exists(self.filename):
                self.file_import = pd.read_csv(self.filename)
                return True
            raise FileNotFoundError
        except FileNotFoundError:
            print("ERROR: Please provide a working CSV file")
            return False

    def close_file(self):
        self.connection.close()

    def convert_file(self):
        """
        This function converts the user's CSV file into a SQL table
        """
        if self.file_import is None:
            print("ERROR: Please provide a working CSV file")
            raise FileNotFoundError

        conn = self.connection
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS flowershopdata')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS "flowershopdata" (
        "Name" TEXT,
        "Description" TEXT,
        "Needs" TEXT,
        "Season" TEXT,
        "Status" TEXT,
        "Date" TEXT,
        "Client_Name" TEXT,
        "Client_phone_number" Text
        )
        ''')

        for row in range(len(self.file_import['Name'])):
            name = self.file_import['Name'][row]
            description = self.file_import['Description'][row]
            needs = self.file_import['Needs'][row]
            season = self.file_import['Season'][row]
            status = self.file_import['Status'][row]
            date = self._convert_datetime(self.file_import['Date'][row])
            client_name = self.file_import['Client Name'][row]
            client_phone = self.file_import['Client phone number'][row]
            cur.execute('''INSERT INTO flowershopdata(Name, Description, 
            Needs, Season, Status, Date, 
            Client_Name, Client_phone_number) VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)''', (name, description,
                                          needs, season, status, date,
                                          client_name, client_phone))
            conn.commit()

    def daily_report(self, specify_year=None, client_history=None):
        with self.connection as con:
            sales_over_time = {}

            if client_history is None:
                rows = self._fetch_table(con)
            else:
                rows = client_history

            for row in rows:
                sale_date = dt.datetime.strptime(row[5], '%Y-%m-%d').date()
                month = sale_date.month
                year = sale_date.year
                day = sale_date.day
                sale_date = dt.date(year, month, day)
                self._add_sale(sale_date=sale_date,
                               sales=sales_over_time,
                               year=year,
                               specify_year=specify_year)

            self._visualize_report(sales=sales_over_time,
                                   specify_year=specify_year,
                                   interval="Daily")

    def monthly_report(self, specify_year=None, client_history=None):
        """
        Uses visualize_sales() function to visualize monthly data of sales
        Also gives information of client past buying history
        """
        with self.connection as con:
            monthly_sales = {}
            if client_history is None:
                rows = self._fetch_table(con)
            else:
                rows = client_history
            # populate dictionary with date values
            for row in rows:
                sale_date = dt.datetime.strptime(row[5], '%Y-%m-%d').date()
                month = sale_date.month
                year = sale_date.year
                first_of_month = dt.datetime(year, month, 1)
                self._add_sale(sale_date=first_of_month,
                               sales=monthly_sales,
                               year=year,
                               specify_year=specify_year)

            self._visualize_report(sales=monthly_sales,
                                   specify_year=specify_year,
                                   interval="Monthly")

    def quarterly_report(self, specify_year=None, client_history=None):
        """Uses visualize_sales() function to visualize quarterly
        data of sales"""

        with self.connection as con:
            quarterly_sales = {"Q1": 0
                , "Q2": 0
                , "Q3": 0
                , "Q4": 0}
            if client_history is None:
                rows = self._fetch_table(con)
            else:
                rows = client_history
            # populate dictionary with date values
            for row in rows:
                sale_date = dt.datetime.strptime(row[5], '%Y-%m-%d').date()
                month = sale_date.month
                year = sale_date.year
                first_of_month = dt.datetime(year, month, 1)
                if 1 <= month <= 3:
                    self._add_sale(sale_date="Q2",
                                   sales=quarterly_sales,
                                   year=year,
                                   specify_year=specify_year)
                elif 4 <= month <= 6:
                    self._add_sale(sale_date="Q2",
                                   sales=quarterly_sales,
                                   year=year,
                                   specify_year=specify_year)
                elif 7 <= month <= 9:
                    self._add_sale(sale_date="Q3",
                                   sales=quarterly_sales,
                                   year=year,
                                   specify_year=specify_year)
                elif 10 <= month <= 12:
                    self._add_sale(sale_date="Q4",
                                   sales=quarterly_sales,
                                   year=year,
                                   specify_year=specify_year)
                else:
                    raise DataNotFound()

            self._visualize_report(sales=quarterly_sales,
                                   specify_year=specify_year,
                                   interval="Quarterly")

    def yearly_report(self, specify_year=None, client_history=None):
        """Uses visualize_sales() function to visualize yearly data"""
        with self.connection as con:
            yearly_sales = {}
            if client_history is None:
                rows = self._fetch_table(con)
            else:
                rows = client_history
            # populate dictionary with date values
            for row in rows:
                sale_date = dt.datetime.strptime(row[5], '%Y-%m-%d').date()
                year = sale_date.year
                self._add_sale(sale_date=str(year),
                               sales=yearly_sales,
                               year=year,
                               specify_year=specify_year)

            self._visualize_report(sales=yearly_sales,
                                   specify_year=specify_year,
                                   interval="Yearly")

    def look_up_client(self, client_search: str, time_interval="daily",
                       specify_year=None):
        """Using user input, queries DB for a clients past buying history
        Returns dictionary of all client sales in the past
        Uses _visualize_data Function to generate a graph of sales history"""
        with self.connection as con:
            table_rows = self._fetch_table(con)
            client_history = []

            for row in table_rows:
                client_name = row[6]
                if client_name == client_search:
                    client_history.append(row)
            if time_interval == 'monthly':
                self.monthly_report(client_history=client_history,
                                    specify_year=specify_year)
            elif time_interval == 'quarterly':
                self.quarterly_report(client_history=client_history,
                                      specify_year=specify_year)
            elif time_interval == 'yearly':
                self.yearly_report(client_history=client_history,
                                   specify_year=specify_year)
            else:
                self.daily_report(client_history=client_history,
                                  specify_year=specify_year)

            return client_history

    def add_new_sale(self, name: str, description: str, needs: str,
                     season: str, status: str, date: dt.date, client_name: str,
                     client_phone_number: str):
        """Queries DB for sales data and adds new sale(s)
        Linked list of sales(s)?"""
        with self.connection as con:
            if type(date) is not dt.date:
                # must be dt format due to other functions
                raise ImproperDataFormat()

            cur = con.cursor()
            query = ("INSERT INTO flowershopdata(Name, Description,"
                     "Needs, Season, Status, Date, Client_Name, "
                     "Client_phone_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")

            val = (name, description, needs, season, status, date, client_name,
                   client_phone_number)
            cur.execute(query, val)
            con.commit()

    def void_sale(self, client_name):
        """
        Uses look_up_client() function to obtain client history
        User is presented with sale(s)
        Then selected history will be removed
        """
        pass

    def _visualize_report(self, sales: dict, specify_year: int, interval: str):
        """
        Helper function for creating reports that basically edits the title
        of the sales table given the specify_year and time interval

        Exception is raised when the year specified does not have
        matching data
        """
        if len(sales) > 0 and specify_year is not None:
            self._visualize_sales(sales, f"{specify_year} {interval}")
        elif len(sales) > 0 and specify_year is None:
            self._visualize_sales(sales, f"{interval}")
        else:
            raise DataNotFound()

    @staticmethod
    def _add_sale(sale_date, sales: dict,
                  year: int, specify_year: int):
        """
        Helper function for creating reports for sales
        Updates given sales dictionary using (key: value) pair of
        (date: number of sales)
        Updates the sales dictionary based on the year specified by user
        """
        if specify_year is not None:
            if year == specify_year:
                if sale_date not in sales:
                    sales[sale_date] = 1
                else:
                    sales[sale_date] += 1
        else:
            if sale_date not in sales:
                sales[sale_date] = 1
            else:
                sales[sale_date] += 1

    @staticmethod
    def _fetch_table(con):
        """Fetches flowershopdata SQL table"""
        cur = con.cursor()
        cur.execute('SELECT * FROM flowershopdata')
        return cur.fetchall()

    @staticmethod
    def _visualize_sales(sales_over_time,
                         specify_title="No specification"):
        """Visualizes sales data using matplotlib"""
        # matplotlib
        fig, ax = plt.subplots()
        dates = sales_over_time.keys()
        sales = sales_over_time.values()

        # defining width of bars in bar graph
        total_dates = len(dates)
        bar_width = 0.8
        if total_dates < 5:  # identifies quarterly period, will need to refactor this later
            bar_width = 1
        elif total_dates < 13:  # basically for months
            bar_width = 5
        elif total_dates < 25:  # daily
            bar_width = 3

        # set labels
        plt.xlabel("Time")
        plt.ylabel("Number of Customer Sales")
        plt.title(f"Customer Sales Over Time ({specify_title})")

        # create bar graph
        ax.bar(dates, sales, color='gold', edgecolor="blue", width=bar_width)
        ax.grid('on')
        plt.xticks(rotation=20)
        plt.subplots_adjust(bottom=0.15)
        ax.set_ylim(0, max(sales) + 1)
        plt.show()

    @staticmethod
    def _convert_datetime(date_string: str) -> date:
        """
        Helper function for convert_file() that takes the "date" column
        within flowershopdata.csv and converts it into a datetime object
        This only is workable with the provided CSV format: Mon. Day, Year
        """

        date_split = date_string.split(",")
        month = date_split[0][:3]
        month = MONTHS[month]
        day = int(date_split[0][4:])
        year = int(date_split[1])
        new_date = dt.date(year, month, day)
        return new_date


def main():
    # Test functions
    file = FlowerDataBase('flowershopdata.csv')
    file.import_file()
    file.convert_file()
    file.daily_report()
    #file.monthly_report()
    '''print(file.look_up_client("Izaiah Levine",
                              time_interval="yearly",
                              specify_year=2016))'''
    #file.quarterly_report(2016)
    #file.yearly_report(2016)
    '''file.add_new_sale("Poppy", "A poppy", "Needs well drained soil",
                      "Blooms mid Spring", "Sold", dt.date(2016, 4, 14),
                      "Meep Moop", "(800) 888-8888")'''
    file.close_file()


if __name__ == '__main__':
    main()
