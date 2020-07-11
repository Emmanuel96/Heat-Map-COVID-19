
# Accessing the UK stringency_data on 6 th April
import matplotlib.pyplot as plt
import json
import urllib.request
import xlsxwriter
import pandas as pd
import numpy as np
import warnings
from matplotlib.collections import QuadMesh
from matplotlib.text import Text



# plot import
import seaborn as sns
sns.set()

# Read excel file and get the stringency sheet
xls = pd.ExcelFile('OXCGRT_summary.xlsx')

confirmed_cases_data = pd.read_excel(xls, 0)
confirmed_cases_data = confirmed_cases_data[:-1]
# --------------- BEGINNING OF QUESTION 4 ----------------------
# iterate from 2nd march to 10th May
# get the countries for our y axis label
countries = confirmed_cases_data['CountryCode']
# drop the country name 
data = confirmed_cases_data.drop(['CountryName'], axis=1)

# next we melt our data
data_melted = data.melt('CountryCode', var_name='dates', value_name="cases")
# array of months 
months = ['jan', 'feb', 'mar', 'apr', 'may']
# we need to create our dataframe of weekly cases
cols = ['CountryCode', 'Weeks', 'Cases']
weekly_cases = pd.DataFrame(columns=cols)
# loop through each country and needed months
endloop = False
for country in countries:
    # start with day 2 and month: index of 2 
    day = 2
    month = 2  # i.e. march starting from 0
    week_count = 1
    week_day_count = 1
    cases_count = 0
    while (endloop == False):
        # if month is March days are 31
        if (month == 2):
            month_str = months[2]  # i.e. march
            max_day = 31
            if (day > max_day):
                # reset day
                day = 1
                month += 1
        elif (month == 3):
            month_str = months[3]  # i.e. april
            max_day = 30
            if (day > max_day):
                day = 1
                month += 1
        elif (month == 4):
            month_str = months[3]  # i.e. may
            max_day = 10
            if (day >= max_day):
                # end loop
                endloop = True
        # we get the date first
        if day < 10:
            day_str = '0' + str(day)
        else:
            day_str = str(day)
        current_date = day_str + month_str + '2020'
        # now we get the cases on this particular day
        is_country = data_melted['CountryCode'] == country
        is_date = data_melted['dates'] == current_date
        # get our particular row
        no_of_cases = data_melted[is_country &
                                  is_date].cases.astype('int64').values[0]
        # increment our case count
        cases_count += no_of_cases

        # When it reaches a week
        if week_day_count == 7:
            # get the average cases count for the week
            cases_count /= 7
            # the only thing left here is to create the new dataframe
            weeks_data_arr = {'CountryCode': country,
                              'Weeks': str(week_count), 'Cases': cases_count}
            weekly_cases = weekly_cases.append(
                weeks_data_arr, ignore_index=True)
            print(weeks_data_arr)
            # increment week count
            week_count += 1
            # increment week day count
            week_day_count = 1
            # reset case count
            case_count = 0
        else:
            week_day_count += 1
        # increment day
        day += 1
    endloop = False

weekly_cases_unmelted = weekly_cases.pivot(
    index="CountryCode", columns="Weeks", values = 'Cases')
weekly_cases_unmleted = weekly_cases_unmelted.reset_index(drop = True)
weekly_cases_unmelted.columns.name = None

# we need to re arrange and sort the wks i.e. wk1, wk2, .....
col_names = ['1','2','3','4','5','6','7','8','9','10']
weekly_cases_unmelted = weekly_cases_unmelted.reindex(columns = col_names)
# create counter and total column
i = 1
weekly_cases_unmelted['Total'] = 0
while i<= 10:
    weekly_cases_unmelted['Total'] += weekly_cases_unmelted[str(i)]
    i += 1

# sort based on total cases and pick top 10 countries
weekly_cases_unmelted= weekly_cases_unmelted.sort_values(by=['Total'],ascending = False).head(10)


# convert total to integer
# weekly_cases_unmelted['Total'] = weekly_cases_unmelted['Total'].astype('int64')

# create masks for the heat map
mask = np.zeros((11,11))
mask[:,10] = True

# create a dataframe to hold the correlation matrix
correlation_df = weekly_cases_unmelted.corr().copy()
# customize x and y axis labels
y_axis_labels = weekly_cases_unmelted.index.tolist()
x_axis_labels = ['03/20','','', '03/27','','','04/03','','','', 'Total']
# draw heat map
ax = sns.heatmap(correlation_df, mask=mask, xticklabels=x_axis_labels,
            vmin = correlation_df.values[:,:10].ravel().min(),
            vmax=correlation_df.values[:, :10].ravel().max(),
                 cbar_kws=dict(use_gridspec=False, location="top"),
                 annot=False, yticklabels=y_axis_labels, fmt="{:,}")
for (j,i), label in np.ndenumerate(weekly_cases_unmelted.values):
    if i == 10:
        ax.text(i+0.7,j+0.7, "{:,}".format(round(label)),
                fontdict=dict(ha='center',va='center',
                                    color='k', fontsize=8))
# set color bar
cbar = ax.collections[0].colorbar
cbar.set_ticks([0,0.5,1])
# cbar.set_location('top')
cbar.set_ticklabels(['0','17.5k', '35k'])
# # move x ticks and label to the top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')
plt.show()
# --------------------- END OF QUESTION 4 -------------------------
