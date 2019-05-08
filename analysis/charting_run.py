from charting import NFLContracts, print_df, df_to_html

c = NFLContracts()

df = c.avg_salary_by_years_left()

print_df(df)
df_to_html(df)

c.close()