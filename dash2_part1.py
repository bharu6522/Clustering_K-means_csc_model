
import dash
from dash import dash_table
from dash import dcc, html, Input, Output

import datetime as dt 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from dash2_part3 import final_ids_data, id_specific_data, merge_columns, data_dict, apr_nov_unique_id_7_df

app = dash.Dash(__name__)

layout_page_1 = html.Div([
    html.H1("Credit Ranking of CSC-VLEs for Apr'23 to Oct'23"),
    dcc.Dropdown(
        id='month-dropdown',
        options=[
            {'label': 'April', 'value': 'april'},
            {'label': 'May', 'value': 'may'},
            {'label': 'June', 'value': 'june'},
            {'label': 'July', 'value': 'july'},
            {'label': 'August', 'value': 'august'},
            {'label': 'September', 'value': 'september'},
            {'label': 'October', 'value': 'october'}
        ],
        value='april',
        clearable=False
    ),
    dcc.Graph(id='scatter-plot'),
    dcc.Graph(id='histogram'),
    dcc.Graph( id= 'bar_tenure_bucket-plot'),
    dcc.Graph(id='box-plot'),
    dcc.Graph(id='pie-plot'),
    dcc.Graph(id='line-plot'),
    dcc.Dropdown(
        id='cscid-number',
        options=[
            {'label': str(i), 'value': i} for i in range(1, 100)
        ],
        value=5,  # Default value
        clearable=False,
        style={'width': '50%'}
    ),
    dcc.Graph(id='funnel-plot-amt'),
    dcc.Dropdown(
        id='scatter-matrix-dropdown',
        options=[
            {'label': 'Amt', 'value': 'amt'},
            {'label': 'Txn', 'value': 'txn'},
            {'label': 'Tenure', 'value': 'tenure'}
        ],
        value=['amt', 'txn'],  # Default values
        multi=True
    ),
    dcc.Graph(id='scatter-matrix')
    
    ])

layout_page_2 = html.Div([
    html.H1('Contineously appearing cscid from april to october'),
    dash_table.DataTable(
        id='id-data-table', 
        columns=[{"name": i, "id": i} for i in final_ids_data.columns], 
        data=final_ids_data.to_dict('records'), 
        style_table={'overflowY': 'auto', 'maxHeight': '400px', 'overflowX': 'auto'},
        fixed_rows={'headers': True},
        style_cell={'textAlign': 'center', 'minWidth': '50px', 'width': '100px', 'maxWidth': '200px'}
    ),
    dcc.Graph(
        id='scatter_plot_id',
        figure=px.scatter(final_ids_data, x='total_txn', y='total_amt', color='category', title='Scatter Plot')
    ),
    dcc.Graph(
        id = 'count_plot_cat',
        figure = px.histogram(final_ids_data, x='category', title= 'count of cscid based on avg cluster category', color= 'category')
        ),
    dcc.Graph(
        id = 'pie_plot_id',
        figure= px.pie(final_ids_data, names='category', values='total_amt', title='category wise distribution based on total_amt for contineously appearing cscid in April to Oct')
        ),
    
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': category, 'value': category} for category in final_ids_data['category'].unique()],
        value=None,
        multi=False
    ),
    html.Br(),
    dash_table.DataTable(
        id='two-data-table',
        columns=[{"name": i, "id": i} for i in final_ids_data.columns],
        data=[],
        filter_action='native',  # Enable native filtering
        page_action='none', # Disable pagination
        style_table={'overflowY': 'auto', 'maxHeight': '400px'}
    ),
    dcc.Graph(id='bar-plot-table-data')
])

# layout for Page 3
layout_page_3 = html.Div([
    html.H1('Credit Ranking of CSC-VLEs by ID'),
    dcc.Input(id='id-input', type='text', placeholder='Enter ID'),
    dash_table.DataTable(id='data-table', columns=[{"name": i, "id": i} for i in id_specific_data.columns], data=[]),
    dcc.Graph(id='linebar_plot_amt_txn'),
    dcc.Graph(id='barplot_amt'),
    dcc.Graph(id='lineplot_amt'),
    dcc.Graph(id='scatterplot_amt_txn'),
    dcc.Graph(id='lineplot_txn'),
    dcc.Graph(id='pieplot_amt')
    
    ])

layout_page_4 = html.Div([
    html.H1('Compare of two vles'),
    html.P('Please Enter the first cscid'), 
    dcc.Input(id='id1-input',type='text', placeholder='Enter first ID'),
    # dash_table.DataTable(id='id1-data-table', columns= [{"name":i, "id": i} for i in id_specific_data.columns], data=[]),
    html.P('Please Enter the second cscid'),
    dcc.Input(id= 'id2-input', type= 'text', placeholder= 'Enter second ID'),
    # dash_table.DataTable(id= 'id2-data-table', columns= [{"name":i, "id":i} for i in id_specific_data.columns], data= []),
    html.H2('combined table for both cscid'),
    dash_table.DataTable(id='combined-data-table', columns=[{"name":i, "id":i} for i in merge_columns], data= []),    
    dcc.Graph(id ='combined-line-fig'),
    dcc.Graph(id= 'line-fig-txn'),
    dcc.Graph(id='scatter-fig-tenure'),
    dcc.Graph(id= 'line-fig-tenure')
    ])

# callback function for Page 1
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('histogram', 'figure'),
     Output('box-plot', 'figure'),
     Output('bar_tenure_bucket-plot','figure'),
     Output('pie-plot', 'figure'),
     Output('line-plot', 'figure'),
     Output('funnel-plot-amt', 'figure'),
     Output('scatter-matrix','figure')
    
     ],
    [Input('month-dropdown', 'value'),
     Input('cscid-number', 'value'),
     Input('scatter-matrix-dropdown','value')]
    )
def update_cluster_plot(selected_month, num_cscid, selected_values):
    
    data_plot = data_dict[selected_month]
    data_plot['ctag'] = data_plot['ctag'].astype('object')
    data_plot['services'] = data_plot['services'].astype('object')
    data_plot['cluster'] = data_plot['cluster'].astype('object')
    
    # Scatter Plot
    scatter_fig = px.scatter(data_plot, x='txn', y='amt', color="cluster", title='Scatter Plot of Amount vs Transaction',hover_data=['cscid']) #hover_data={'amt': True, 'txn': True}
    
    agg_hist_df_grp_ctag = data_plot.groupby(['cluster','ctag']).agg({'amt': 'sum'}).reset_index()
    hist_fig = px.bar(agg_hist_df_grp_ctag, x='ctag',y='amt',color="cluster", title='Sum of amt by ctag')
    hist_fig.update_xaxes(
    tickvals=[3, 4, 5],  # Set the positions of the ticks
    ticktext=['B', 'A', 'A+']  # Set the labels for the ticks
    )
    
    agg_hist_grp_ctag = data_plot.groupby(['ctag','cluster']).agg({'cscid': 'count'}).reset_index()
    hist_ctag_fig = px.bar(agg_hist_grp_ctag, x='ctag', y='cscid', color='cluster', title='count of cscid by ctag')
    hist_ctag_fig.update_xaxes(
    tickvals=[3, 4, 5],  # Set the positions of the ticks
    ticktext=['B', 'A', 'A+']  # Set the labels for the ticks
    )
    
    agg_sum_amt_grp_bucket = data_plot.groupby(['tenure_bucket']).agg({'amt': 'sum','txn': 'sum'}).reset_index()
    # bar_tenure_bucket_fig = px.bar(agg_sum_amt_grp_bucket, x='tenure_bucket', y='amt',barmode='group', color= 'cluster', title= f'tenure_bucket wise distribution of amt in {selected_month}')
    
    bar_tenure_bucket_fig = go.Figure()
    bar_tenure_bucket_fig.add_trace(go.Bar(x= agg_sum_amt_grp_bucket['tenure_bucket'], y= agg_sum_amt_grp_bucket['amt'], name='amt', marker_color='blue'))
    bar_tenure_bucket_fig.add_trace(go.Scatter(x=agg_sum_amt_grp_bucket['tenure_bucket'], y=agg_sum_amt_grp_bucket['txn'], mode='lines+markers', name='txn', yaxis='y2'))
    bar_tenure_bucket_fig.update_layout(title= f'tenure_bucket wise distribution of amt and txn variation for {selected_month} month', yaxis_title='amt', yaxis2=dict(title='txn', overlaying='y', side='right'))
    
    
    
    agg_bar_grp_ctag = data_plot.groupby('cluster').agg({'tenure': 'median'}).reset_index()
    pie_fig = go.Figure(data=[go.Pie(labels=agg_bar_grp_ctag['cluster'], values=agg_bar_grp_ctag['tenure'])])
    pie_fig.update_layout(title='Cluster with tenure median')
    # box_fig = px.box(data_plot, x='cluster', y='amt', title='Box Plot of Amount by Cluster') #hover_data={'amt': True}
    
    agg_line_grp_cluster = data_plot.groupby('cluster').agg({'amt': 'sum', 'txn': 'sum'}).reset_index()
    line_fig = make_subplots(specs=[[{"secondary_y": True}]])
    line_fig.add_trace(go.Scatter(x=agg_line_grp_cluster['cluster'], y=agg_line_grp_cluster['amt'], mode='lines', name='sum of amt'),secondary_y=False)  
    line_fig.add_trace(go.Scatter(x=agg_line_grp_cluster['cluster'], y=agg_line_grp_cluster['txn'], mode='lines', name='sum of txn'), secondary_y=True)
    line_fig.update_layout(title='Line plot for amt and txn', xaxis_title='Cluster', yaxis_title='Sum of amt', yaxis2_title = 'Sum of txn')
    line_fig.update_xaxes(
    tickvals=[0, 1, 2, 3],  # Set the positions of the ticks
    ticktext=['0', '1', '2', '3']  # Set the labels for the ticks
    )
    
    # funnel chart 
    sorted_data_amt = data_plot.nlargest(num_cscid, 'amt')
    funnel_fig_amt = px.funnel(sorted_data_amt, x='amt', y='cscid', labels={'amt': 'Amount', 'cscid': 'CSCID'}, title=f'Top {num_cscid} CSCID by Amount')
    scatter_matrix_fig = px.scatter_matrix(data_plot, dimensions=selected_values, color="cluster", title = f'scatter matrix for id {selected_month}')
    
    return scatter_fig, hist_fig, hist_ctag_fig, bar_tenure_bucket_fig, pie_fig, line_fig, funnel_fig_amt, scatter_matrix_fig
    
# Callback function for page 2 
@app.callback(
    [Output('two-data-table', 'data'),
     Output('bar-plot-table-data','figure')
      ],
    [Input('category-dropdown', 'value')]
    )
def cscid_table(selected_category):
    
    if selected_category is not None:
        filtered_data = final_ids_data[final_ids_data['category'] == selected_category]
        new_data = filtered_data.to_dict('records')  # Convert DataFrame to list of dictionaries
        
        # Create bar plot
        bar_fig = px.bar(filtered_data, x='cscid', y='total_amt', title= f'Total Amount for CSCID having category as {selected_category}')
        bar_fig.update_xaxes(title='CSCID')
        bar_fig.update_yaxes(title='Total Amount')
        
        return new_data, bar_fig 
    else:
        empty_figure = px.scatter(title='No Data Available').update_layout(showlegend=False)
        return [], empty_figure

#  callback function for page 3
@app.callback(
    [Output('data-table', 'data'),
     Output('linebar_plot_amt_txn','figure'),
     Output('barplot_amt', 'figure'),
     Output('lineplot_amt', 'figure'),
     Output('scatterplot_amt_txn','figure'),
     Output('lineplot_txn','figure'),
     Output('pieplot_amt', 'figure'),
     # Output('histplot_tenure', 'figure')
     ],
    [Input('id-input', 'value')]
)
def update_id_plots(selected_id):
    # Check if selected_id is not None and convert it to string
    table_data = []
    if selected_id is not None:
        selected_id = str(selected_id)
        
        # Check if selected_id exists in cscid column
        if selected_id in apr_nov_unique_id_7_df['cscid'].values:
            id_plot = id_specific_data[id_specific_data['cscid'] == selected_id]
            # id_plot['avg_cluster'] = id_plot['avg_cluster'].astype('str')
            id_plot['ctag'] = id_plot['ctag'].astype('str')
            id_plot['services'] = id_plot['services'].astype('str')
            id_plot['cluster'] = id_plot['cluster'].astype('str')
            
            table_data = id_plot.to_dict('records')
            
            # Line chart with column
            line_with_column = go.Figure()
            line_with_column.add_trace(go.Bar(x=id_plot['month'], y=id_plot['amt'], name='amt', marker_color='blue'))
            line_with_column.add_trace(go.Scatter(x=id_plot['month'], y=id_plot['txn'], mode='lines+markers', name='txn', yaxis='y2'))
            line_with_column.update_layout(title= f'amt and txn variation for id {selected_id}', yaxis_title='amt', yaxis2=dict(title='txn', overlaying='y', side='right'))
            
            #  bar plots 
            bar_amt_plot = px.bar(id_plot,x='month',y='amt',title=f"monthly distribution of sum of amt for id {selected_id}", color='cluster')
            
            # Line plots 
            # line_amt_plot = px.line(id_plot,x='month',y='amt',markers=True)
            line_amt_plot = make_subplots(specs=[[{"secondary_y": True}]])
            line_amt_plot.add_trace(go.Scatter(x=id_plot['month'], y= id_plot['amt'], mode='lines', name='sum of amt'),secondary_y=False)  
            line_amt_plot.add_trace(go.Scatter(x=id_plot['month'], y= id_plot['txn'], mode='lines', name='sum of txn'), secondary_y=True)
            line_amt_plot.update_layout(title= f'Line plot for amt and txn for id {selected_id}', xaxis_title='month', yaxis_title='Sum of amt', yaxis2_title = 'Sum of txn')
        
            line_txn_plot = px.line(id_plot, x='month', y='cluster',title= f"monthly distribution of clusters for id {selected_id}")
            
            # Scatter plot 
            scatter_fig = px.scatter(id_plot, x='txn', y='amt', color="ctag",size='amt', title='Scatter Plot of Amount vs Transaction',color_continuous_scale='Viridis', hover_data=['month']) #hover_data={'amt': True, 'txn': True}
            
            pie_plot = go.Figure(data=[go.Pie(labels=id_plot['month'], values=id_plot['amt'])])
            pie_plot.update_layout(title='distribution of amt')
           
          
            return table_data,line_with_column ,bar_amt_plot, line_amt_plot, scatter_fig, line_txn_plot, pie_plot    #month_cluster_bar #avg_cluster_bar, 
    
    # If selected_id is None or not found in the DataFrame, return empty figures
    empty_figure = px.scatter(title='No Data Available').update_layout(showlegend=False)
    return table_data, empty_figure, empty_figure, empty_figure, empty_figure, empty_figure, empty_figure
                
@app.callback(
    [
      # Output('id1-data-table', 'data'),
      # Output('id2-data-table', 'data'),
      Output('combined-data-table', 'data'),
      Output('combined-line-fig','figure'),
      Output('line-fig-txn','figure'),
      Output('scatter-fig-tenure','figure'),
      Output('line-fig-tenure', 'figure')
     ],
    [Input('id1-input', 'value'),
     Input('id2-input','value')]
)
def comapre_ids(id1, id2):
    
    # id1_table_data = []
    # id2_table_data = []
    combined_table_data = []
    flag1, flag2 = False, False  
    if id1 is not None :
        flag1 = True  
    
    if id2 is not None :
        flag2 = True  
    
    if (flag1) and (flag2):
        id1 = str(id1)
        id2 = str(id2)
        # Check if selected_id exists in cscid column
        if (id1 in apr_nov_unique_id_7_df['cscid'].values) and (id2 in apr_nov_unique_id_7_df['cscid'].values) :
            id_data_1 = id_specific_data[id_specific_data['cscid'] == id1]
            id_data_2 = id_specific_data[id_specific_data['cscid'] == id2]
            # id_plot['avg_cluster'] = id_plot['avg_cluster'].astype('str')
            id_data_1['ctag'] = id_data_1['ctag'].astype('str')
            id_data_1['services'] = id_data_1['services'].astype('str')
            id_data_1['cluster'] = id_data_1['cluster'].astype('str')
            
            id_data_2['ctag'] = id_data_2['ctag'].astype('str')
            id_data_2['services'] = id_data_2['services'].astype('str')
            id_data_2['cluster'] = id_data_2['cluster'].astype('str')
            
            id_data_1.rename(columns={'cscid': 'cscid1', 'amt':'amt1', 'txn':'txn1', 'ctag':'ctag1', 'tenure':'tenure1', 'dcode_rank':'dcode_rank1', 'services': 'services1', 'cluster':'cluster1', 'tenure_bucket':'tenure_bucket1'}, inplace= True)
            id_data_2.rename(columns={'cscid': 'cscid2', 'amt':'amt2', 'txn':'txn2', 'ctag':'ctag2', 'tenure':'tenure2', 'dcode_rank':'dcode_rank2', 'services': 'services2', 'cluster':'cluster2', 'tenure_bucket':'tenure_bucket2'}, inplace= True)
     
            id_df = pd.merge(id_data_1, id_data_2, on= 'month')
            
            combined_table_data = id_df.to_dict('records')
            
            line_fig = make_subplots(specs=[[{"secondary_y": False}]])
            line_fig.add_trace(go.Scatter(x= id_df['month'], y= id_df['amt1'], mode='lines', name= f'amt for cscid {id1}'),secondary_y=False)  
            line_fig.add_trace(go.Scatter(x= id_df['month'], y= id_df['amt2'], mode='lines', name= f'amt for cscid {id2}')) #, secondary_y=True
            line_fig.update_layout(title= f'comparison of amt for cscid {id1} and cscid {id2}', xaxis_title='Month', yaxis_title='amt for cscid1') #, yaxis2_title = 'amt for cscid2 '
            
            line_fig_txn = make_subplots(specs=[[{"secondary_y": False}]])
            line_fig_txn.add_trace(go.Scatter(x= id_df['month'], y= id_df['txn1'], mode='lines', name= f'amt for cscid {id1}'),secondary_y=False)  
            line_fig_txn.add_trace(go.Scatter(x= id_df['month'], y= id_df['txn2'], mode='lines', name= f'amt for cscid {id2}'))  #, secondary_y=True
            line_fig_txn.update_layout(title= f'comparison of txn for cscid {id1} and cscid {id2}', xaxis_title='Month', yaxis_title='txn for cscid1') #, yaxis2_title = 'txn for cscid2 '
            
            line_fig_tenure = make_subplots(specs=[[{"secondary_y": False}]])
            line_fig_tenure.add_trace(go.Scatter(x= id_df['month'], y= id_df['tenure1'], mode='lines', name= f'tenure for cscid {id1}'),secondary_y=False)  
            line_fig_tenure.add_trace(go.Scatter(x= id_df['month'], y= id_df['tenure2'], mode='lines', name= f'tenure for cscid {id2}'))  #, secondary_y=True
            line_fig_tenure.update_layout(title= f'comparison of tenure for cscid {id1} and cscid {id2}', xaxis_title='Month', yaxis_title='tenure for cscid') #, yaxis2_title = 'txn for cscid2 '
            
            scatter_fig_amt1 = px.scatter(id_df, 
                              x='month', 
                              y='amt1', 
                              color='cscid1', 
                              title='Scatter Plot of Amount 1 vs Month', 
                              hover_data=['cscid1'])
            
            scatter_fig_amt2 = px.scatter(id_df, 
                              x='month', 
                              y='amt2', 
                              color='cscid2', 
                              title='Scatter Plot of Amount 2 vs Month', 
                              hover_data=['cscid2'])
            
            combined_fig = scatter_fig_amt1.update_traces(marker=dict(symbol='circle'))
            for trace in scatter_fig_amt2.data:
                combined_fig.add_trace(trace).update_traces(marker=dict(symbol='square'))  # Assign square symbol for amt2

            # Assigning different colors
            combined_fig.data[0].marker.color = 'blue'  # Color for amt1
            combined_fig.data[1].marker.color = 'red'   # Color for amt2

            return combined_table_data, line_fig, line_fig_txn, combined_fig, line_fig_tenure # no_rename_id1_data, no_rename_id2_data, 
            
    empty_figure = px.scatter(title='No Data Available').update_layout(showlegend=False)
    return combined_table_data, empty_figure, empty_figure, empty_figure #id1_table_data, id2_table_data, 


# Define a callback to render different layouts based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-1':
        return layout_page_1
    elif pathname == '/page-2':
        return layout_page_2 
    elif pathname == '/page-3':
        return layout_page_3
    elif pathname == '/page-4':
        return layout_page_4 
    else:
        return '404 - Page not found'


# Define the main layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
    