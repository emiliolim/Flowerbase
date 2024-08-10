"""
Emilio Lim
8/7/24

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
"""
import pandas as pd
import sqlite3 as sql
from dataclasses import dataclass
import datetime as dt

MONTHS = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
}


class DataNotFound(Exception):
    pass


@dataclass
class FileManager:
    filename: str = None
    file_import: pd.DataFrame = None

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

        conn = sql.connect("flowershopdata.sqllite3")
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
            date = self.file_import['Date'][row]
            client_name = self.file_import['Client Name'][row]
            client_phone = self.file_import['Client phone number'][row]
            cur.execute('''INSERT INTO flowershopdata(Name, Description, 
            Needs, Season, Status, Date, 
            Client_Name, Client_phone_number) VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)''', (name, description,
                                          needs, season, status, date,
                                          client_name, client_phone))
            conn.commit()

    def _convert_datetime(self):
        """
        Helper function for convert_file() that takes the "date" column
        within flowershopdata.csv and converts it into a datetime object
        This only is workable with the provided CSV format: Mon. Day, Year
        """
        for row in range(len(self.file_import['Date'])):
            date = self.file_import['Date'][row]
            date_split = date.split(",")
            month = date_split[0][:3]
            month = MONTHS[month]
            print(month)


    def visualize_sales(self):
        """Visualizes sales data using matplotlib"""
        pass

    def look_up_client(self):
        """Using user input, queries DB for a clients past buying history"""
        pass

    def monthly_report(self):
        """Uses visualize_sales() function to visualize monthly data of sales
        Also gives information of client past buying history"""
        pass

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


def main():
    file = FileManager('flowershopdata.csv')
    file.import_file()
    #print(file.file_import)
    #file.convert_file()
    file._convert_datetime()


if __name__ == '__main__':
    main()
