from dash2_part1 import Base

def Credit_Monthly(date8,tenure_res_date):

    base_instance = Base()
    monthly_overall_data = base_instance.fetch_service_monthly_data(date8,tenure_res_date) 
    resultant_df = base_instance.remove_outlier(monthly_overall_data)
    resultant_df = base_instance.mapping_db(resultant_df)
    resultant_df = base_instance.kmeans_apply(resultant_df)

    return resultant_df



