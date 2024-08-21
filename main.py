"""
Emilio Lim
8/7/24
Python 3.6.2
Latest version of Matplotlib, Pandas, and SQLite3

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
from datetime import date

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


@dataclass
class FlowerDataBase:
    filename: str = None
    file_import: pd.DataFrame = None
    connection: sql.Connection = sql.connect('flowershopdata.sqlite')

    def import_file(self):
        """
        Initializes file import into readable format for Python
        ***MUST*** include .csv or .sql extension
        """
        try:
            self.file_import = pd.read_csv(self.filename)
            return True
        except FileNotFoundError:
            print('File not found')
            return False

    def convert_file(self):
        """
        This function converts the user's CSV file into a SQL table
        """
        if self.file_import is None:
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
                               specify_year=specify_year)

            self._visualize_report(sales=monthly_sales,
                                   specify_year=specify_year,
                                   interval="Monthly")

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
    def _add_sale(sale_date: dt.date, sales: dict, specify_year: int):
        """
        Helper function for creating reports for sales
        Updates given sales dictionary using (key: value) pair of
        (date: number of sales)
        Updates the sales dictionary based on the year specified by user
        """
        year = sale_date.year
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
            else:
                self.daily_report(client_history=client_history,
                                  specify_year=specify_year)
            return client_history

    def quarterly_report(self):
        """Uses visualize_sales() function to visualize quarterly
        data of sales"""
        pass

    def yearly_report(self):
        """Uses visualize_sales() function to visualize yearly data"""
        pass

    def add_new_sale(self):
        """Queries DB for sales data and adds new sale(s)
        Linked list of sales(s)?"""
        pass

    @staticmethod
    def _fetch_table(con):
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
        if total_dates < 12:
            bar_width = 5
        elif total_dates < 25:
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
    #print(file.look_up_client("Izaiah Levine",
                              #time_interval="monthly",
                              #specify_year=2016))


if __name__ == '__main__':
    main()
