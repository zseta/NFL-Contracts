import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


def df_ready(df):
    return df is not None


def print_df(df):
    if df_ready(df):
        print df.to_string()


def df_to_html(df):
    if df_ready(df):
        df.to_html("temp.html")
        print "HTML created!"


class NFLContracts(object):

    def __init__(self):
        self.conn = pymysql.connect(host="localhost",
                           user="root",
                           passwd="root",
                           db="nfl_contracts",
                           unix_socket="/opt/lampp/var/mysql/mysql.sock",
                           charset='utf8', use_unicode=True)

    def close(self):
        self.conn.close()

    def describe(self):
        query = ("SELECT age, avg_year AS yearly_salary, free_agency_year, fully_guaranteed, total_guaranteed, total_value FROM Contract")
        df = pd.read_sql(query, self.conn)
        d = {'Mean': df.mean(),
             'Min': df.min(),
             'Max': df.max(),
             'Median': df.median()}
        print query
        return pd.DataFrame.from_dict(d, dtype='int32')[["Min", "Max", "Mean", "Median"]].transpose()

    def min_max_salaries(self, mode="min"):
        mode = "ASC" if mode == "min" else "DESC"
        query = ("SELECT player, age, position, team, avg_year AS yearly_salary, free_agency_year FROM Contract "
                 "ORDER BY avg_year " + mode + " LIMIT 5")
        return pd.read_sql(query, self.conn)

    def longest_contract(self):
        query = ("SELECT player, age, position, team, avg_year, free_agency_year FROM Contract "
                 "ORDER BY free_agency_year DESC LIMIT 4")
        return pd.read_sql(query, self.conn)

    def contract_year_dist(self):
        query = ("SELECT (free_agency_year-2019) AS contract_length FROM Contract")
        df = pd.read_sql(query, self.conn)
        df[["contract_length"]].plot(kind="hist", bins=range(0, 8), color="orange")
        plt.ylabel("Number of players")
        plt.xlabel("Remaining years of the contract")
        plt.show()

    def age_contract_length_corr(self):
        query = ("SELECT age, AVG(free_agency_year-2019) AS contract_length "
                 "FROM Contract WHERE age IS NOT NULL "
                 "GROUP BY age ORDER BY age ASC")
        df = pd.read_sql(query, self.conn)
        df.plot(kind="line", x="age", y="contract_length", color="red")
        plt.ylabel("Average remaining years of contract")
        plt.show()

    def age_contract_length_scat(self):
        query = ("SELECT age, (free_agency_year-2019) AS contract_length "
                 "FROM Contract WHERE age IS NOT NULL ORDER BY age ASC")
        df = pd.read_sql(query, self.conn)
        x = df['age'].tolist()
        y = df['contract_length'].tolist()
        c = Counter(zip(x, y))
        s = [10 * c[(xx, yy)] for xx, yy in zip(x, y)]
        df.plot(kind="scatter", x="age", y="contract_length", s=s, color="blue")
        plt.show()

    def age_dist(self):
        query = ("SELECT age FROM Contract WHERE age IS NOT NULL")
        df = pd.read_sql(query, self.conn)
        df[["age"]].plot(kind="hist", bins=range(20, 50), xticks=range(20, 50, 2), color="teal")
        plt.ylabel("Number of players")
        plt.xlabel("Age")
        plt.show()

    def avg_by_positions(self):
        query = ("SELECT position, AVG(avg_year) AS avg_yearly_salary FROM Contract GROUP BY position ORDER BY avg_yearly_salary DESC")
        df = pd.read_sql(query, self.conn)
        ax = plt.gca()
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        df.plot(kind="bar", x="position", y="avg_yearly_salary", color="royalblue", ax=ax, grid=True)
        plt.xlabel("Position")
        plt.ylabel("Yearly Salary")
        plt.show()

    def age_by_position(self):
        query = ("SELECT position, COUNT(*) player_count, SUM(CASE WHEN age <= 24 THEN 1 ELSE 0 END) as young_count, "
                 "SUM(CASE WHEN (age >= 25 AND age <= 30) THEN 1 ELSE 0 END) as middle_count, "
                 "SUM(CASE WHEN age >= 31 THEN 1 ELSE 0 END) as old_count "
                 "FROM Contract WHERE age IS NOT NULL GROUP BY position")
        df = pd.read_sql(query, self.conn)

        totals = [i + j + k for i, j, k in zip(df['young_count'], df['middle_count'], df['old_count'])]
        young = [i / j * 100 for i, j in zip(df['young_count'], totals)]
        middle = [i / j * 100 for i, j in zip(df['middle_count'], totals)]
        old = [i / j * 100 for i, j in zip(df['old_count'], totals)]

        positions = df["position"].tolist()
        r = range(0,len(positions))
        barWidth = 0.85
        plt.bar(r, young, color='#b5ffb9', edgecolor='white', width=barWidth)
        plt.bar(r, middle, bottom=young, color='#f9bc86', edgecolor='white', width=barWidth)
        plt.bar(r, old, bottom=[i + j for i, j in zip(young, middle)], color='#a3acff', edgecolor='white',
                width=barWidth)

        plt.xticks(r, positions)
        plt.ylabel("%")
        plt.legend(["21-24 year olds", "25-30 year olds", "31+ year olds"], loc=1)

        plt.show()

    def expensive_positions(self):
        query = ("SELECT team, position, SUM(avg_year) AS yearly_salary FROM Contract GROUP BY team, position "
                 "ORDER BY yearly_salary DESC LIMIT 5")
        return pd.read_sql(query, self.conn)

    def last_year_salary(self):
        query = ("SELECT (free_agency_year-2019) AS years_left, avg_year FROM Contract")
        df = pd.read_sql(query, self.conn)
        x = df['years_left'].tolist()
        y = df['avg_year'].tolist()
        c = Counter(zip(x, y))
        s = [20 * c[(xx, yy)] for xx, yy in zip(x, y)]
        ax = plt.gca()
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        df.plot(kind="scatter", x="years_left", y="avg_year",
                yticks=range(500000, 25000000, 500000), s=s, color="violet", ax=ax, grid=True)
        plt.show()

    def age_avg_year(self):
        query = ("SELECT age, avg_year AS yearly_salary FROM Contract WHERE age IS NOT NULL")
        df = pd.read_sql(query, self.conn)
        x = df['age'].tolist()
        y = df['yearly_salary'].tolist()
        c = Counter(zip(x, y))
        s = [20 * c[(xx, yy)] for xx, yy in zip(x, y)]
        ax = plt.gca()
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        df.plot(kind="scatter", x="age", y="yearly_salary",
                yticks=range(500000, 25000000, 1000000), s=s, color="plum", ax=ax, grid=True)
        plt.show()

    def avg_salary_by_years_left(self):
        query = ("SELECT (free_agency_year-2019) AS years_left, FLOOR(AVG(avg_year)) AS avg_yearly_salary "
                 "FROM Contract GROUP BY years_left")
        df = pd.read_sql(query, self.conn)
        ax = plt.gca()
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        df.plot(kind="line", x="years_left", y="avg_yearly_salary", color="red", ax=ax)
        plt.show()
