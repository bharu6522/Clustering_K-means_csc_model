import pandas as pd
import pymongo 

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import  KMeans


class Base:
    
    def  __init__(self):

        try:
            client = pymongo.MongoClient("server_connection")
           
        except pymongo.errors.ServerSelectionTimeoutError as err :
            print (err)
        
        self.db = client['collection_name'] ### Configuration Database

     
    def fetch_service_monthly_data(self,date8,tenure_res_date):

        april_data = self.db.monthly_overall_dim_cscid.aggregate([{"$match":{"recorddate":{"$eq": date8},"nature":True,"grid":{"$ne":1},"ctag":{"$nin":["Z","C","D"]}}},
                            {"$project":{"_id":0,
                                        "cscid":1, 
                                        "txn":1,
                                        "amt": 1,
                                        "dcode":1,
                                        "scode":1,
                                        "recorddate":1,
                                        "ctag":1
                                    
                                        }}])

        monthly_overall_banking_data = self.db.monthly_bank_dim_cscid.aggregate([{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True, "ctag":{"$nin":["Z","C","D"]}}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        monthly_overall_banking_data = pd.DataFrame(list(monthly_overall_banking_data))
        monthly_overall_digipay_data = self.db.monthly_dp_all_dim_cscid.aggregate(
                        [{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True, "ctag":{"$nin":["Z","C","D"]}}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        monthly_overall_digipay_data = pd.DataFrame(list(monthly_overall_digipay_data))
        dsp_insurance_gi = self.db.monthly_dsp_dim_cscid_serviceid.aggregate(
                        [{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True, "ctag":{"$nin":["Z","C","D"]},"serviceid":1}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        
        dsp_insurance_gi = pd.DataFrame(list(dsp_insurance_gi))

        dsp_insurance_Li = self.db.monthly_dsp_dim_cscid_serviceid.aggregate(
                        [{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True, "ctag":{"$nin":["Z","C","D"]},"serviceid":3}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        
        dsp_insurance_Li = pd.DataFrame(list(dsp_insurance_Li))
        
        insurance_renewal_df = self.db.monthly_dsp_dim_cscid_serviceid.aggregate(
                        [{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True,"ctag":{"$nin":["Z","C","D"]},"serviceid":2}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        insurance_renewal_df = pd.DataFrame(list(insurance_renewal_df))
        
        loan_emi_collection = self.db.monthly_dsp_dim_cscid_serviceid.aggregate(
                        [{"$match":{"recorddate":{"$eq":date8},"grid":{"$ne":1},"nature": True,"ctag":{"$nin":["Z","C","D"]},"serviceid":49}},
                         {"$project":{"_id":0,
                                    "cscid":1,
                                    "recorddate":1
                                    }}])
        loan_emi_collection = pd.DataFrame(list(loan_emi_collection))

        overall_df = pd.DataFrame(list(april_data)).copy()
        monthly_overall_data = overall_df[:]

        overall_df.dropna(inplace=True)
        grouped_data = overall_df.groupby('dcode')['cscid'].count().reset_index()
        grouped_data.columns = ['dcode', 'count_id']
        grouped_data.sort_values(by='count_id')
        new_df = pd.merge(overall_df, grouped_data, on='dcode', how='left')
        new_df = new_df[(new_df['amt']>=0)&(new_df['txn']>=0)]


        new_df['amt_z'] = (new_df['amt'] - new_df['amt'].mean()) / new_df['amt'].std()
        new_df['txn_z'] = (new_df['txn'] - new_df['txn'].mean()) / new_df['txn'].std()
        new_df['count_id_z'] = (new_df['count_id'] - new_df['count_id'].mean()) / new_df['count_id'].std()
        new_df['avg_z'] = new_df[['amt_z', 'txn_z', 'count_id_z']].mean(axis=1)
        # new_df_ranked = new_df.sort_values(by='avg_z', ascending=False)[['dcode', 'avg_z']]

        min_rank = 1
        max_rank = 738  # Assuming you want the rank to be between 1 and the number of distrcit 

        new_df['rank'] = ((new_df['avg_z'] - new_df['avg_z'].min()) / (new_df['avg_z'].max() - new_df['avg_z'].min())) * (max_rank - min_rank) + min_rank
        new_df['rank'] = new_df['rank'].round().astype(int)

        filtered_df = new_df[(new_df['rank'] >= 1) & (new_df['rank'] <= 738)]

        scode_result_df = filtered_df[['dcode', 'rank']].drop_duplicates(subset='dcode')

        # Process for rdate removal which are null , nan or invalid 
        vle_rdate_cursor = self.db.cscspv_vle_list.find({}, {"_id": 0, "cscid": 1, "rdate": 1})
        vle_rdate_df = pd.DataFrame(list(vle_rdate_cursor))     # Convert the list of dictionaries to a DataFrame
        monthly_overall_data = monthly_overall_data.merge(vle_rdate_df, on='cscid', how='left').dropna(subset=['rdate'])
        
        monthly_overall_data['rdate'] = pd.to_datetime(monthly_overall_data['rdate'], errors='coerce')
        monthly_overall_data = monthly_overall_data.dropna(subset=['rdate'])
        monthly_overall_data = monthly_overall_data[monthly_overall_data['rdate'] != '']
        
        dummy_id_check = monthly_overall_data[monthly_overall_data['cscid'].isin(monthly_overall_data['cscid'].value_counts()[monthly_overall_data['cscid'].value_counts() > 1].index)]
        monthly_overall_data = monthly_overall_data.merge(dummy_id_check, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

        monthly_overall_data['tenure'] = tenure_res_date - monthly_overall_data['rdate']
        
        monthly_overall_data = monthly_overall_data.merge(scode_result_df, on='dcode')

        # result_df_overall = merged_df_scode_all.sort_values(by='rank')
        monthly_overall_data.rename(columns={'rank':'dcode_rank'}, inplace=True)

        monthly_overall_data['banking'] = monthly_overall_data['cscid'].isin(monthly_overall_banking_data['cscid']).map({True: 'Yes', False: 'No'})
        monthly_overall_data['digipay'] = monthly_overall_data['cscid'].isin(monthly_overall_digipay_data['cscid']).map({True: 'Yes', False: 'No'})
        monthly_overall_data['dsp_insurance_gi'] = monthly_overall_data['cscid'].isin(dsp_insurance_gi['cscid']).map({True: 'Yes', False: 'No'})
        
        if dsp_insurance_Li.shape == (0,0):
            dsp_insurance_Li = pd.DataFrame(columns=['cscid','recorddate'])

        monthly_overall_data['dsp_insurance_Li'] = monthly_overall_data['cscid'].isin(dsp_insurance_Li['cscid']).map({True: 'Yes', False: 'No'})
        monthly_overall_data['loan_emi_collection'] = monthly_overall_data['cscid'].isin(loan_emi_collection['cscid']).map({True: 'Yes', False: 'No'})
        monthly_overall_data['insurance_renewal_df'] = monthly_overall_data['cscid'].isin(insurance_renewal_df['cscid']).map({True: 'Yes', False: 'No'})

        self.monthly_overall_data = monthly_overall_data

        return monthly_overall_data

    def categorize_tenure(self,tenure):
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
    
    def remove_outlier(self,result_df_overall):

        result_df_overall.dropna(inplace=True)
        # result_df_overall['tenure'] = result_df_overall['tenure'].dt.days.astype(int)
        result_df_overall['tenure'] = result_df_overall['tenure'].apply(lambda x: x.days).astype(int)
        result_df_overall['amt'] = result_df_overall['amt'].astype('int64')
        result_df_overall['tenure_bucket'] = result_df_overall['tenure'].apply(self.categorize_tenure)
        result_df_overall = result_df_overall[result_df_overall['amt']>= 0 & (result_df_overall['txn']>=0)]
    
        # removing outlier based on txn
        Q1 = result_df_overall['txn'].quantile(0.25)
        Q3 = result_df_overall['txn'].quantile(0.75)
        IQR = Q3 - Q1

        result_df_overall = result_df_overall[(result_df_overall['txn'] >= Q1 - 1.5 * IQR) & (result_df_overall['txn'] <= Q3 + 1.5 * IQR)]
        result_df_overall['tenure_bucket'] = result_df_overall['tenure_bucket'].astype('int64')

        return result_df_overall

    def mapping_db(self, result_df_overall):
    
        custom_mapping = {'A+': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
        result_df_overall['ctag'] = result_df_overall['ctag'].map(custom_mapping)
        yes_no_mapping = {'Yes': 1, 'No': 0}
        result_df_overall['banking'] = result_df_overall['banking'].map(yes_no_mapping)
        result_df_overall['digipay'] = result_df_overall['digipay'].map(yes_no_mapping)
        result_df_overall["dsp_insurance_gi"] = result_df_overall["dsp_insurance_gi"].map(yes_no_mapping)
        result_df_overall["dsp_insurance_Li"] = result_df_overall["dsp_insurance_Li"].map(yes_no_mapping)
        result_df_overall["insurance_renewal_df"] = result_df_overall["insurance_renewal_df"].map(yes_no_mapping)
        result_df_overall["loan_emi_collection"] = result_df_overall["loan_emi_collection"].map(yes_no_mapping)

        result_df_overall['services'] = result_df_overall[['banking','digipay','dsp_insurance_Li','dsp_insurance_gi','insurance_renewal_df','loan_emi_collection']].sum(axis=1)
        result_df_overall = result_df_overall.drop(columns=['recorddate','rdate','scode','dcode','tenure_bucket','banking','digipay','dsp_insurance_Li','dsp_insurance_gi','insurance_renewal_df','loan_emi_collection'],axis=1)
        
        return result_df_overall
    
    def kmeans_apply(self, result_df_overall):
    
        # Data preprocessing
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(result_df_overall[['amt','txn','ctag', 'dcode_rank', 'tenure', 'services']])
        num_clusters = 4  # Replace with your desired number of clusters
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(scaled_data)
        y_data = kmeans.fit_predict(scaled_data)
        result_df_overall['cluster'] = y_data

        return result_df_overall
    






























        