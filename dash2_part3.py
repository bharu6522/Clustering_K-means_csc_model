from dash2_part2 import Credit_Monthly
import datetime as dt 
import pandas as pd


month_list = ['april','may','june','july','august','september','october']
date8 = dt.datetime(2023,4,1)
tenure_res_date = dt.datetime(2023,4,30)
date_list = [] # for storing date 
tenure_res_list = []

while date8.month < 11:
    date_list.append((date8.year, date8.month, 1))  # Append the date with day fixed at 1 to the date_list
    date8 = date8.replace(month=date8.month + 1) # Move to the next month
    tenure_res_date = date8 - dt.timedelta(days=date8.day)
    tenure_res_list.append(tenure_res_date)


date_list = [dt.datetime(*date_tuple) for date_tuple in date_list]

data_after_modelling_april = Credit_Monthly(date_list[0],tenure_res_list[0])
data_after_modelling_may= Credit_Monthly(date_list[1],tenure_res_list[1])
data_after_modelling_june  = Credit_Monthly(date_list[2],tenure_res_list[2])
data_after_modelling_july = Credit_Monthly(date_list[3],tenure_res_list[3])
data_after_modelling_august  = Credit_Monthly(date_list[4], tenure_res_list[4])
data_after_modelling_september  = Credit_Monthly(date_list[5], tenure_res_list[5])
data_after_modelling_october = Credit_Monthly(date_list[6],tenure_res_list[6])


month_list = ['april','may','june','july','august','september','october']

data_dict = {
    'april': data_after_modelling_april,
    'may': data_after_modelling_may,
    'june': data_after_modelling_june,
    'july': data_after_modelling_july,
    'august': data_after_modelling_august,
    'september': data_after_modelling_september,
    'october': data_after_modelling_october
    }

def categorize_tenure(tenure):
            if tenure >= 0 and tenure <= 90:
                return 1
            elif tenure >= 91 and tenure <= 180:
                return 2
            # Add more conditions for additional buckets if needed
            elif tenure >= 181 and tenure <= 365:
                return 3
            elif tenure>=361 and tenure <= 730:
                return 4
            elif tenure >=731 and tenure <=1825:
                return 5
            else :
                return 6



for month,df in data_dict.items():
    # df['tenure_bucket'] = df['tenure'].apply(base_instance.categorize_tenure())
    df['tenure_bucket'] = df['tenure'].apply(lambda x: categorize_tenure(x))



dfs_with_month = []

for month, df in data_dict.items():
    df['month'] = month  # Add a new column 'month' with the month name
    dfs_with_month.append(df)

result_df_month = pd.concat(dfs_with_month, ignore_index=True)
result_df_month['cscid'] = result_df_month['cscid'].astype('str')


def count_recorddates(series):
    return series.count()

# Define a custom aggregation function to sum values for each cscid
def sum_values(series):
    return series.sum()

grouped_data = result_df_month.groupby('cscid').agg(
    count_of_month=('month', count_recorddates),
    amt_sum =('amt', sum_values),  # Sum of 'amt' column
    txn_sum =('txn', sum_values)   # Sum of 'txn' column
).reset_index()



# only ids with count 7 
apr_nov_unique_id_7 = grouped_data[grouped_data['count_of_month']== 7]['cscid']
apr_nov_unique_id_7_df = apr_nov_unique_id_7.to_frame().reset_index()

data_count_7_allMonth = pd.merge(result_df_month, apr_nov_unique_id_7_df, on='cscid', how='right')
data_count_7_allMonth.drop(columns = 'index',inplace=True)
data_count_7_allMonth['cluster'] = data_count_7_allMonth['cluster'].astype('str')

mapping = {
    'april': {'2': 4, '3': 3, '1': 2, '0': 1},
    'may': {'3': 4, '0': 3, '1': 2, '2': 1},
    'june': {'2': 4, '3': 3, '1': 2, '0': 1},
    'july': {'3': 4, '1': 3, '2': 2, '0': 1},
    'august': {'3': 4, '1': 3, '2': 2, '0': 1},
    'september': {'1': 4, '0': 3, '3': 2, '2': 1},
    'october': {'0': 4, '1': 3, '2': 2, '3': 1}
}


data_count_7_allMonth['cluster_mark'] = data_count_7_allMonth.apply(lambda row: mapping[row['month']][row['cluster']], axis=1)

final_ids_data = data_count_7_allMonth.groupby('cscid').agg(
    sum_of_cluster_marks = ('cluster_mark', sum_values),
    sum_of_amt = ('amt', sum_values),
    sum_of_txn = ('txn', sum_values),
    number_of_services = ('services', sum_values)
    ).reset_index()

def category_ranking(mark):
    
    if mark >= 21 :
        return 'Premium'
    elif (mark < 21) and (mark >= 14) :
        return 'Standard'
    elif (mark < 14) and (mark >= 7) :
        return 'Basic'
    else:
        return 'Non Preferred'

final_ids_data['category'] = final_ids_data['sum_of_cluster_marks'].apply(category_ranking)

id_specific_data = pd.merge(final_ids_data,result_df_month,on='cscid', how='left')
id_specific_data.drop(columns=['sum_of_cluster_marks','sum_of_amt','sum_of_txn','number_of_services','category'],inplace=True)

final_ids_data.drop(columns=['sum_of_cluster_marks'],inplace= True)
final_ids_data.rename(columns={'sum_of_amt': 'total_amt','sum_of_txn': 'total_txn'},inplace= True)
final_ids = pd.merge(apr_nov_unique_id_7_df, final_ids_data, on= 'cscid', how='left')

merge_columns = ['cscid1', 'amt1', 'txn1', 'ctag1', 'tenure1', 'dcode_rank1', 'services1',
       'cluster1', 'month', 'tenure_bucket1','cscid2', 'amt2', 'txn2', 'ctag2', 'tenure2', 'dcode_rank2', 'services2',
              'cluster2', 'tenure_bucket2']


