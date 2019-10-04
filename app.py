#!/usr/bin/env python
# coding: utf-8

# ## <center>dash oil and gas</center>
# 
# Dash Oil and Gas uses Plotly Dash components, and classes within the ```dgrid_components``` module, to recreate the Dash Gallery webpage https://dash-gallery.plotly.host/dash-oil-and-gas/.

# In[ ]:


import os
import io

import dgrid_components as dgc  # @UnresolvedImport


# In[ ]:


import copy
import pickle
import datetime as dt
import pandas as pd
import flask
# from flask import app

html = dgc.html
# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS  # @UnresolvedImport


# #### Establish path to data

# In[ ]:


DATA_PATH = os.path.abspath('./data')
# DROPBOX_PATH = "/pyStuff/jp_notebooks/like_dash_oil_and_gas/data"
# DATA_PATH = DROPBOX_PATH


class MainApp():
    def __init__(self):
        # Create controls
        county_options = [{"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES]
        well_status_options = [{"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}for well_status in WELL_STATUSES]
        well_type_options = [{"label": str(WELL_TYPES[well_type]), "value": str(well_type)}for well_type in WELL_TYPES]
        # This is taken from Dash Project 
        df1 = pd.read_csv(os.path.join(DATA_PATH,"wellspublic.csv"), low_memory=False)
#         df1 = get_df_from_dropbox(os.path.join(DATA_PATH,"wellspublic.csv"))
#         df1 = get_df_from_dropbox(DATA_PATH + "/wellspublic.csv")
        df1["Date_Well_Completed"] = pd.to_datetime(df1["Date_Well_Completed"])
        df1 = df1[df1["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]
        df1['Year_Well_Completed'] = df1.Date_Well_Completed.apply(lambda d: d.year)
        df1['Month_Well_Completed'] = df1.Date_Well_Completed.apply(lambda d: d.month)
        self.df1 = df1.copy()

        trim = df1[["API_WellNo", "Well_Type", "Well_Name"]]
        trim.index = trim["API_WellNo"]
        dataset = trim.to_dict(orient="index")
        points = pickle.load(open(os.path.join(DATA_PATH,"points.pkl"), "rb"))
#         points = get_pickle_from_dropbox(os.path.join(DATA_PATH,"points.pkl"))
#         points = get_pickle_from_dropbox(DATA_PATH+"/points.pkl")
        tgas = 'Gas Produced, MCF'
        twater = 'Water Produced, bbl'
        toil = 'Oil Produced, bbl'
        dict_list = [{'API_WellNo':k,'year':y,'gas':points[k][y][tgas],'water':points[k][y][twater],'oil':points[k][y][toil]} for k in points.keys() for y in points[k].keys()]
        df_points = pd.DataFrame(dict_list)
        df_points['all_types'] = df_points.gas + df_points.water + df_points.oil
        self.df_points = df_points.copy()

        df_county = pd.DataFrame({'Cnty':[int(s) for s in list(COUNTIES.keys())],'cname':list(COUNTIES.values())})
        df2 = df1.merge(df_county,on='Cnty',how='inner')
    #     print(len(df2))
        df_well_status = pd.DataFrame({
            'Well_Status':list(WELL_STATUSES.keys()),
            'wstatus':list(WELL_STATUSES.values())})
        df2 = df2.merge(df_well_status,on='Well_Status',how='inner')
        df_well_type = pd.DataFrame({'Well_Type':list(WELL_TYPES.keys()),'wtype':list(WELL_TYPES.values())})
        df2 = df2.merge(df_well_type,on='Well_Type',how='inner')
        df_well_color = pd.DataFrame({'Well_Type':list(WELL_COLORS.keys()),'wcolor':list(WELL_COLORS.values())})
        df2 = df2.merge(df_well_color,on='Well_Type',how='inner')
        df = df2.copy()
        self.df = df.copy()

        
        # Define the static components
        # ********************** plotly logo ****************************
        img = html.Img(src=dgc.dash.Dash().get_asset_url("dash-logo.png"),className='plogo')
        # ********************** title div ********************************
        title = html.Div([html.H3("New York Oil And Gas",className='ogtitle'),html.H5("Production Overview",className='ogtitle')])
        # *****You ************* link to plotly info ***********************
        adiv = html.A([html.Button(["Learn More"],className='ogabutton')],href="https://plot.ly/dash/pricing",className='adiv')
        
        
        
        # build row 2, column1 components that help you build your main data store
        # ********************* slider *********************************
        text_slider = html.Div(['Filter by construction date (or select range in histogram):',html.P()])
        yr_slider = dgc.RangeSliderComponent('yr_slider',text_slider,min_value=df.Year_Well_Completed.min(),max_value=df.Year_Well_Completed.max())
        slider = html.Div(yr_slider.html,className='r2_margin')
        
        # ********************* well status radio *****************************
        rs_op=[{'label': 'All', 'value': 'all'},{'label': 'Active only', 'value': 'active'},{'label': 'Customize', 'value': 'custom'}]
        radio_status = dgc.RadioItemComponent('radio_status',html.Div(['Filter by well status:',html.P()]),rs_op,'active',style={})
        radio1 = html.Div([radio_status.html],className='r2_margin')
        
        # ********************* well status dropdown *****************************
        ds_op = well_status_options
        self.ds_op = ds_op.copy()

        ws_keys = [d['value'] for d in ds_op]
        
        dropdown_status = dgc.DropdownComponent('dropdown_status','',ds_op,ws_keys,
            input_tuples=[(radio_status.id,'value')],callback_input_transformer=self._select_well_status_list)
        dropdown1 = html.Div(dropdown_status.html,className='d1_margin')
        
        # ********************* well type radio *********************************
        rt_op=[{'label': 'All', 'value': 'all'},{'label': 'Productive only', 'value': 'productive'},{'label': 'Customize', 'value': 'custom'}]
        radio_type = dgc.RadioItemComponent('radio_type',html.Div(['Filter by well type:',html.P()]),rt_op,'productive',style={})
        radio2 = html.Div([radio_type.html],className='r2_margin')
        
        # ********************* dropdown for well type *********************************
        dt_op = well_type_options
        wt_keys = [d['value'] for d in dt_op]

        self.ws_keys = ws_keys
        self.wt_keys = wt_keys
        
        dropdown_type = dgc.DropdownComponent('dropdown_type','',dt_op,wt_keys,input_tuples=[(radio_type.id,'value')],
            callback_input_transformer=self._select_well_type_list)
        dropdown2 = html.Div(dropdown_type.html,className='d1_margin')
        
        # ********************* build the main_data component **********************
        lg = dgc.init_root_logger()
        input_component_list = [(yr_slider.id,'value'),(dropdown_status.id,'value'),(dropdown_type.id,'value')]
        main_data = dgc.StoreComponent('store_df',input_component_list=input_component_list,
                        create_storage_dictionary_from_inputs_callback=lambda v:self._build_main_data_dictionary(v,logger=lg))
        self.main_data = main_data
        main_data.create_storage_dictionary_from_inputs_callback = lambda v:self._build_main_data_dictionary(v,logger=lg)
        
        
        
        aggs_div_comps = [self._make_agg_div(tc) for tc in ['no_wells','gas_mcf','oil_bbl','water_bbl']]
        
        # build the panels
        wells = html.Div([aggs_div_comps[0].html,html.P('Wells')])
        gas = html.Div([aggs_div_comps[1].html,html.P('Gas')])
        oil = html.Div([aggs_div_comps[2].html,html.P('Oil')])
        water = html.Div([aggs_div_comps[3].html,html.P('Water')])
        
        xygraph = dgc.XyGraphComponent('xygraph',main_data,x_column='Year_Well_Completed',num_x_values=8,
            title='Completed Wells/Year',transform_input=lambda value_list:_trans_df(value_list))
        
        
        
        # ************* Build row 3: the map and pie charts ********************************
        mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"
        
        self.basic_layout = dict(
            autosize=True,
            automargin=True,
            margin=dict(l=30, r=30, b=20, t=40),
            hovermode="closest",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            legend=dict(font=dict(size=10), orientation="h"),
            title="Satellite Overview",
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style="light",
                center=dict(lon=-78.05, lat=42.54),
                zoom=7,
            ),
        )        
        
        mapgraph = dgc.FigureComponent('mapgraph',None,self._create_map_figure,input_tuple_list=input_component_list)
        piegraph = dgc.FigureComponent('piegraph',None,self._create_pie_figure,input_tuple_list=input_component_list)
        
        
        
        callback_components = [yr_slider,radio_status,radio_type,dropdown_status,dropdown_type,main_data,xygraph,mapgraph,piegraph] + aggs_div_comps
        
        
        pn = 'rpanel'
        pnnc = 'rpanelnc'
        r1 = dgr('r1',[img,title,adiv],child_class=pnnc)
        r2c1 = dgr('r2c1',[slider,radio1,dropdown1,radio2,dropdown2],child_class=pnnc)
        r2c2r1 = dgr('r2c2r1',[wells,gas,oil,water],child_class=pn,parent_class=pnnc)
        r2c2r2 = dgr('r2c2r2',[xygraph.html])
        r2c2r3 = html.Div()
        r2c2 = dgr('r2c2',[r2c2r1,r2c2r2,r2c2r3],child_class=None,parent_class=pnnc)
        r2 = dgr('r2',[r2c1,r2c2])
        r3 = dgr('r3',[mapgraph.html,html.Div(' '),piegraph.html],parent_class=pnnc)
        rbot = dgr('rbot',['the bottom'],child_class=pn)
        rside = html.Div(' ')
        rall_rows = dgr('rall_rows',[r1,r2,r3,rbot])
        rall_cols = dgr('rall_cols',[rside,rall_rows,rside],parent_class=pnnc)

#         server = flask.Flask(__name__)
#         app = dgc.dash.Dash(__name__, server=server)
        
#         self.app = dgc.dash.Dash(__name__)
#         self.app = dgc.dash.Dash(__name__, url_base_pathname='/dev/')
        self.app = dgc.dash.Dash(__name__)
        self.app.layout = html.Div([rall_cols,main_data.html])
        for c in callback_components:
            c.callback(self.app)
    
    def run_server(self):
        self.app.run_server()

    def _build_df_from_input_list(self,input_list,logger=None):
        year_list = input_list[0]
        year_low = int(str(year_list[0]))
        year_high = int(str(year_list[1]))
        df_temp = self.df[(self.df.Year_Well_Completed>=year_low) & (self.df.Year_Well_Completed<=year_high)]
        status_list = input_list[1] 
        type_list = input_list[2]
        try:
            df_temp = df_temp[df_temp.Well_Status.isin(status_list)]
            df_temp = df_temp[df_temp.Well_Type.isin(type_list)]
        except Exception as e:
            if logger is not None:
                logger.warn(f'EXCEPTION: _build_main_data_dictionary {str(e)}')
        return df_temp

    def _build_main_data_dictionary(self,input_list,logger=None):
        year_list = input_list[0]
        year_low = int(str(year_list[0]))
        year_high = int(str(year_list[1]))
        df_temp = self._build_df_from_input_list(input_list,logger)
        df_temp2 = df_temp[["API_WellNo", "Year_Well_Completed"]].groupby(['Year_Well_Completed'],as_index=False).count()
        #{'wells': 14628, 'gas': 865.4, 'water': 15.8, 'oil': 3.8}
        aggs = self.get_well_aggregates(df_temp,[year_low,year_high])
        ret = {
            'data':df_temp2.to_dict('rows'),
            'no_wells':f"{aggs['wells']} No of",
            'gas_mcf':f"{aggs['gas']}mcf",
            'oil_bbl':f"{aggs['oil']}M bbl",
            'water_bbl':f"{aggs['water']}M bbl"
        }
        return ret


    def get_well_aggregates(self,df,year_array,well_status_list=None,well_type_list=None):
        df_temp = df[(df.Year_Well_Completed>=year_array[0]) & (df.Year_Well_Completed<=year_array[1])]
        df_ptemp = self.df_points[(self.df_points.year>=year_array[0])&(self.df_points.year<=year_array[1])]
        df_ptemp = df_ptemp[df_ptemp.API_WellNo.isin(df_temp.API_WellNo.unique())]
        if well_status_list is not None:
            valid_status_ids = self.df1[self.df1.Well_Status.isin(well_status_list)].API_WellNo.values
            df_ptemp = df_ptemp[df_ptemp.API_WellNo.isin(valid_status_ids)]
        if well_type_list is not None:
            valid_type_ids = self.df1[self.df1.Well_Type.isin(well_type_list)].API_WellNo.values
            df_ptemp = df_ptemp[df_ptemp.API_WellNo.isin(valid_type_ids)]
        wells = len(df_temp.API_WellNo.unique())
        agg_data =  {
            'wells':wells,
            'gas':round(df_ptemp.gas.sum()/1000000,1),
            'water':round(df_ptemp.water.sum()/1000000,1),
            'oil':round(df_ptemp.oil.sum()/1000000,1)
        }
        return agg_data
        

    def _select_well_status_list(self,input_list):
        k =  input_list[0]
#         print(f'this is k: {k}')
        if k.lower()=='all':
            ret = [self.ws_keys]
        elif k.lower()=='active':
            i = self.ws_keys.index('AC')
            ret = [[self.ds_op[i]['value']]]
        else:
            ret = [[]]
        return ret
    
    def _select_well_type_list(self,input_list):
        k =  input_list[0]
#         print(f'this is k: {k}')
        if k.lower()=='all':
            ret = [self.wt_keys]
        elif k.lower()=='productive':
            ret = [["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]]
        else:
            ret = [[]]
        return ret

    def _make_agg_div(self,agg_name):
        text_comp = dgc.DivComponent(agg_name,input_component=self.main_data,
            callback_input_transformer=lambda value_list:_get_main_data(value_list,agg_name),style={'margin':'0px'})
        return text_comp

    def _create_map_figure(self,input_list):
        graph_layout = copy.deepcopy(self.basic_layout)
        
        dff = self._build_df_from_input_list(input_list)
        traces = []
        for well_type, dfff in dff.groupby("Well_Type"):
            trace = dict(
                type="scattermapbox",
                lon=dfff["Surface_Longitude"],
                lat=dfff["Surface_latitude"],
                text=dfff["Well_Name"],
                customdata=dfff["API_WellNo"],
                name=WELL_TYPES[well_type],
                marker=dict(size=4, opacity=0.6),
            )
            traces.append(trace)
    
        figure = dict(data=traces, layout=graph_layout)
        return figure
    
    def _create_pie_figure(self,input_list):
        layout_pie = copy.deepcopy(self.basic_layout)
        dff = self._build_df_from_input_list(input_list)
        selected = dff["API_WellNo"].values
        
        years = input_list[0]
        year_low = years[0]
        year_high = years[1]
        aggs = self.get_well_aggregates(dff,[year_low,year_high])
    
        index = aggs['wells']
        gas = aggs['gas']
        oil = aggs['oil']
        water = aggs['water']
        
        aggregate = dff.groupby(["Well_Type"]).count()
    
        data = [
            dict(
                type="pie",
                labels=["Gas", "Oil", "Water"],
                values=[gas, oil, water],
                name="Production Breakdown",
                text=[
                    "Total Gas Produced (mcf)",
                    "Total Oil Produced (bbl)",
                    "Total Water Produced (bbl)",
                ],
                hoverinfo="text+value+percent",
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
                domain={"x": [0, 0.45], "y": [0.2, 0.8]},
            ),
            dict(
                type="pie",
                labels=[WELL_TYPES[i] for i in aggregate.index],
                values=aggregate["API_WellNo"],
                name="Well Type Breakdown",
                hoverinfo="label+text+value+percent",
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
                domain={"x": [0.55, 1], "y": [0.2, 0.8]},
            ),
        ]
        layout_pie["title"] = "Production Summary: {} to {}".format(
            year_low, year_high
        )
        layout_pie["font"] = dict(color="#777777")
        layout_pie["legend"] = dict(
            font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
        )
    
        figure = dict(data=data, layout=layout_pie)
        return figure
    

def get_from_dropbox(file_path):
    acctok = open('./temp_folder/dropbox_at.txt','r').read()
    import dropbox
    dbx = dropbox.Dropbox(acctok)
    metadata, result = dbx.files_download(path=file_path)
    return metadata,result

def get_pickle_from_dropbox(file_path):
    metadata,result = get_from_dropbox(file_path)  # @UnusedVariable
    bytes_file = io.BytesIO(result.content)
    ret = pickle.load(bytes_file)
    return ret    

def get_df_from_dropbox(file_path):
    metadata,result = get_from_dropbox(file_path)  # @UnusedVariable
    text_file = io.StringIO(result.content.decode())
    df = pd.read_csv(text_file)    
    return df    





# ************************** Build row 2, column 2 *************************
# ************* Build row 2, column2, row 1: aggregate data panels ********************************
def _get_main_data(value_list,key):
    value = value_list[0][key]
    return [value]


# ************** Build row 2, column 2, row 2: The main Bar Graph *******************************
def _trans_df(value_list):
    df_ret = pd.DataFrame(value_list['data'])
    return df_ret

def dgr(my_id,children,parent_class=None,child_class=None):
    return html.Div([html.Div(c,className=child_class) for c in children],id=my_id,className=parent_class)


app = MainApp().app
server = app.server
    
if __name__=='__main__':
    app.run_server()

