import pandas as pd
import plotly.express as px
import numpy as np
import datamanager as dm

def main():
    #generate_excel_analysis()
    generate_chart(1658998647, False, True)

def generate_chart(brain_name = None, savehtml = False, x_axis_dates = False):
    data_connection =  dm.get_sql_connection(dm.DATA_PATH)
    df = pd.read_sql_query("SELECT * from trades where id = '{}'".format(brain_name), data_connection)
    # brainzz = "'1656273974','1656260801','1656321672','1656320533','1656262218','1656263567','1656260645','1656322501','1656248933','1656326071','1656275896','1656330812','1656242588','1656273782','1656279292','1656257798','1656318850','1656318797','1656228132','1656235311'"
    # df = pd.read_sql_query("SELECT * from trades where id in ({})".format(brainzz), data_connection)
    #df = pd.read_sql_query("SELECT * from trades where id in (SELECT id from brains where strategy_id = 'RSIADX')".format(brain_name), data_connection)

    df.sort_values(by=['close_date'], inplace=True)
    df = df.reset_index(drop=True)
    df['id'] = df['id'].astype(str)
    df['cumsum'] = df.groupby('id')['result'].cumsum()
    #df['cumsum'] = df['result'].cumsum()
    if x_axis_dates:
        df['close_date'] = df['close_date'].astype('datetime64[ns]')
        chrt = px.line(df,x='close_date', y='cumsum', color='id')
    else: chrt = px.line(df,x=df.index, y='cumsum', color = 'id')

    if savehtml: chrt.write_html(dm.CHART_PATH+brain_name+".html")
    else: chrt.show()

def generate_excel_analysis():
    data_connection =  dm.get_sql_connection(dm.DATA_PATH)
    df = pd.read_sql_query("SELECT * from statistics", data_connection)
    data_connection.close()
    df['winrate'] = df['wins'] / (df['wins'] + df['losses'])
    df['expectancy'] = df['winrate'] + (1-df['winrate'])*(df['avg_loss']/df['avg_gain'])
    df['dd_wght_expectancy'] = df['expectancy'] / -df['mdd']
    df['avg_gain_pertrade'] = df['realized'] / (df['wins'] + df['losses'])
    df['mdd_recovery_rate'] = -df['mdd'] / df['avg_gain_pertrade']
    df['mdd_gain_ratio'] = df['realized'] / -df['mdd']
    df.to_excel("analysis - {}.xlsx".format(dm.get_timestamp()))

if __name__ == "__main__":
    main()

