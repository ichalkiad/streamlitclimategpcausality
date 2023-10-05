"""
Author: Ioannis Chalkiadakis, ISC-PIF/CNRS 
Date:   September 2023
Email:  ioannis.chalkiadakis@cnrs.fr
Copyright Ioannis Chalkiadakis

"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pathlib
import numpy as np
import plotly.express as px
from PIL import Image



if __name__ == '__main__':

    cwd = pathlib.Path.cwd() 
    base_path = "./data/" 
    causaltype = "meancov"
    lag = 1
    quarter_ends = pd.date_range("01/01/2022", "12/31/2022", freq='Q')
    selected_points1 = []
    selected_points2 = []
    selected_points3 = []
    selected_points4 = []

    st.set_page_config(layout="wide", page_title='Statistical causal relationships in the Twitter climate discourse')
    
    technical = st.toggle("Technical format")
    if technical:
        st.title("Gaussian Process-based statistical causal relationships in the 2022 climate Twittersphere")
    else:
        st.title("Statistical causal relationships in the 2022 climate Twittersphere")
    st.header("A case study on quantifying the impact of Twitter discourse, measured by a text-based, daily time-series sentiment signal, "\
                 "on the user activity of different communities, "\
                 "measured by the daily number of Tweets.")
    st.subheader("Ioannis Chalkiadakis, David Chavalarias, ISC-PIF/CRNS, 2023.")
    st.write("The radar plots contain the output of a statistical hypothesis test for statistical causal relationships between two time-series signals."\
             " The closer the color trace is to 1, the more evidence there is to reject the null hypothesis of lack of causal relationships. If the trace "\
                "is below the 0.9 ring, there is a lack of statistically significant evidence to reject the null hypothesis.")
    
    
    with st.container():
        col1, col2, col3 = st.columns(3)

        col1a, col1b = col1.columns(2)
        community = col1a.radio("User community:", options=["Pro-climate", "Denialists"])
        if community == "Pro-climate":
            com = "pro"
            color = px.colors.qualitative.Light24[17]
        elif community == "Denialists":
            com = "contra"
            color = px.colors.qualitative.Light24[0]

        col2a, col2b = col2.columns(2)
        if technical:
            tweets2sent = col2b.select_slider("Impact direction:", options=["Sentiment time-series → Tweets num", "Tweets num → Sentiment time-series"])
        else:
            tweets2sent = col2b.select_slider("Impact direction:", options=["Discourse → user activity", "User activity → discourse"])
        if technical:
            lag = col1b.radio("Lags (days) in the GP model:", options=[1,3,5])
        else:
            lag = col1b.radio("Timescale (days):", options=[1,3,5])
        if technical and (not tweets2sent):
            causalname = col2a.radio("Causal relationships (Sentiment -> Tweets number) measured in the:", options=["GP mean", "GP mean & covariance"])
        elif technical and tweets2sent:
            causalname = col2a.radio("Causal relationships (Tweets number -> Sentiment) measured in the:", options=["GP mean", "GP mean & covariance"])
        elif (not technical) and (not tweets2sent):
            causalname = col2a.radio("Causality-driven factor:", options=["User activity level", "User activity fluctuation"])
        elif (not technical) and tweets2sent:
            causalname = col2a.radio("Causality-driven factor:", options=["Discourse intensity level", "Discourse intensity fluctuation"])

        if causalname=="User activity level" or causalname=="GP mean" or causalname=="Discourse intensity level":
            causaltype = "mean"
        elif causalname=="User activity fluctuation" or causalname=="GP mean & covariance" or causalname=="Discourse intensity fluctuation":
            causaltype = "meancov"
        if tweets2sent=="Discourse → user activity" or tweets2sent=="Sentiment time-series → Tweets num":
            causal_yx = pd.read_csv("{}/{}_Sentiment2{}climtweets_lag{}.csv".format(base_path, 
                                                                            causaltype, com, lag))  
            print("{}/{}_Sentiment2{}climtweets_lag{}.csv".format(base_path, 
                                                                            causaltype, com, lag))
        elif tweets2sent=="User activity -> discourse" or tweets2sent=="Tweets num → Sentiment time-series":
            # actually loading xy
            causal_yx = pd.read_csv("{}/{}_{}climtweets2Sentiment_lag{}.csv".format(base_path, 
                                                                            causaltype, com, lag))  
            print("{}/{}_{}climtweets2Sentiment_lag{}.csv".format(base_path, 
                                                                            causaltype, com, lag))
    with st.container():
        col1, col2 = st.columns(2)
        col1aa, col1ab = col1.columns(2)
               
        with col1aa:
            st.header("2022 - Q1")        
            causal_yx["EndDate"] = causal_yx["EndDate"].apply(pd.to_datetime)
            causal_yx["year_quarter"] = [pd.to_datetime(row["EndDate"]).to_period("Q") for _,row in causal_yx.iterrows()]
            radar_data = causal_yx.loc[causal_yx['year_quarter'] == '2022Q1']
            x = radar_data["EndDate"]
            xstr = [pd.Timestamp(i).strftime('%d/%m/%Y') for i in radar_data["EndDate"].values]
            xangle = np.arange(0, 365, 4)
            xdates = pd.date_range("01/01/2022", quarter_ends[0], freq='D')
            y = radar_data['1minusp']
            xx = []
            if len(x) > 0:
                for i in range(len(x)):
                    idx = np.argwhere(xdates==x[x.index[i]]).flatten()
                    xx.append(xangle[idx][0])

            fig1 = go.Figure(data=go.Scatterpolar(
                                r=y,
                                theta=xx, 
                                mode='lines',
                                line_color=color,
                                fill='toself', text="Ukraine War start"
                                ))
            
            fig1.update_layout(
                template="plotly_dark",
                polar = dict(
                    radialaxis = dict(range=[0, 1], showticklabels=True, tickmode = 'array', tickvals=[0,0.9,1]),
                    angularaxis = dict(showticklabels=True, tickmode = 'array', tickvals=xx, ticktext=xstr)),
                margin=go.layout.Margin(
                            l=35, #left margin
                            r=35, #right margin
                            b=35, #bottom margin
                            t=35, #top margin
                        ),
                font_size=14
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col1ab:
            st.header("\n")
            st.image("{}/q1.png".format(base_path), use_column_width=True, caption="Image sources: The Guardian, DW News, Statista")

        col2aa, col2ab = col2.columns(2)
        with col2aa:
            st.header("2022 - Q2")
            radar_data = causal_yx.loc[causal_yx['year_quarter'] == '2022Q2']
            x = radar_data["EndDate"]
            xstr = [pd.Timestamp(i).strftime('%d/%m/%Y') for i in radar_data["EndDate"].values]
            xangle = np.arange(0, 365, 4)
            xdates = pd.date_range(quarter_ends[0]+pd.DateOffset(1), quarter_ends[1], freq='D')
            y = radar_data['1minusp']
            xx = []
            if len(x) > 0:
                for i in range(len(x)):
                    idx = np.argwhere(xdates==x[x.index[i]]).flatten()
                    xx.append(xangle[idx][0])

            fig2 = go.Figure(data=go.Scatterpolar(
                                r=y,
                                theta=xx, 
                                mode='lines',
                                line_color=color,
                                fill='toself', text="EU State of Climate report 2021"
                                ))
            fig2.update_layout(
                template="plotly_dark",
                polar = dict(
                    radialaxis = dict(range=[0, 1], showticklabels=True, tickmode = 'array', tickvals=[0,0.9,1]),
                    angularaxis = dict(showticklabels=True, tickmode = 'array', tickvals=xx, ticktext=xstr)),
                margin=go.layout.Margin(
                           l=35, #left margin
                            r=35, #right margin
                            b=35, #bottom margin
                            t=35, #top margin
                        ),
                font_size=14
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2ab:
            st.header("")
            st.image("{}/q2.png".format(base_path), use_column_width=True, caption="Image sources: EUMetStat, Copernicus Climate Change Service")
                            
    with st.container():
        col1, col2 = st.columns(2)
        col1aa, col1ab = col1.columns(2)
        with col1aa:
            st.header("2022 - Q3")
            radar_data = causal_yx.loc[causal_yx['year_quarter'] == '2022Q3']
            x = radar_data["EndDate"]
            xstr = [pd.Timestamp(i).strftime('%d/%m/%Y') for i in radar_data["EndDate"].values]
            xangle = np.arange(0, 365, 4)
            xdates = pd.date_range(quarter_ends[1]+pd.DateOffset(1), quarter_ends[2], freq='D')
            y = radar_data['1minusp']
            xx = []
            if len(x) > 0:
                for i in range(len(x)):
                    idx = np.argwhere(xdates==x[x.index[i]]).flatten()
                    xx.append(xangle[idx][0])

            fig3 = go.Figure(data=go.Scatterpolar(
                                r=y,
                                theta=xx, 
                                mode='lines',
                                line_color=color,
                                fill='toself', text="Global Heatwave, US climate legislation, Major gas leak in North Sea"
                                ))
            fig3.update_layout(
                template="plotly_dark",
                polar = dict(
                    radialaxis = dict(range=[0, 1], showticklabels=True, tickmode = 'array', tickvals=[0,0.9,1]),
                    angularaxis = dict(showticklabels=True, tickmode = 'array', tickvals=xx, ticktext=xstr)),
                margin=go.layout.Margin(
                            l=35, #left margin
                            r=35, #right margin
                            b=35, #bottom margin
                            t=35, #top margin
                        ),
                font_size=14
            )
            st.plotly_chart(fig3, use_container_width=True)
            
        with col1ab:
            st.header("\n")
            st.image("{}/q3.png".format(base_path), use_column_width=True, caption="Image sources: Le Monde, Wikipedia, The New York Times, DW News")

        col2aa, col2ab = col2.columns(2)
        with col2aa:
            st.header("2022 - Q4")
            radar_data = causal_yx.loc[causal_yx['year_quarter'] == '2022Q4']
            x = radar_data["EndDate"]
            xstr = [pd.Timestamp(i).strftime('%d/%m/%Y') for i in radar_data["EndDate"].values]
            xangle = np.arange(0, 365, 4)
            xdates = pd.date_range(quarter_ends[2]+pd.DateOffset(1), "12/31/2022", freq='D')
            y = radar_data['1minusp']
            xx = []
            if len(x) > 0:
                for i in range(len(x)):
                    idx = np.argwhere(xdates==x[x.index[i]]).flatten()
                    xx.append(xangle[idx][0])
            fig4 = go.Figure(data=go.Scatterpolar(
                                r=y,
                                theta=xx, 
                                mode='lines',
                                line_color=color,
                                fill='toself', text="COP27, Musk Twitter takeover"
                                ))           
            fig4.update_layout(
                template="plotly_dark",
                polar = dict(
                    radialaxis = dict(range=[0, 1], showticklabels=True, tickmode = 'array', tickvals=[0,0.9,1]),
                    angularaxis = dict(showticklabels=True, tickmode = 'array', tickvals=xx, ticktext=xstr)),
                margin=go.layout.Margin(
                            l=35, #left margin
                            r=35, #right margin
                            b=35, #bottom margin
                            t=35, #top margin
                        ),
                font_size=14
            )
            st.plotly_chart(fig4, use_container_width=True)            
        with col2ab:
            st.header("\n")
            st.image("{}/q4.png".format(base_path), use_column_width=True, caption="Image sources: L'Opinion, ActuEnvironnement, VennGage, MediaPost, The Telegraph")

            
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.subheader("References:")
    st.write("Zaremba AB, Peters GW. Statistical Causality for Multivariate Nonlinear Time Series via Gaussian Process Models. Methodology and Computing in Applied Probability. 2022;24(4):2587-632.")
    st.write("Zaremba AB. Assessing causality in financial time series. UCL (University College London); 2022.")
    st.write("Chalkiadakis, I., Yan, H., Peters, G.W. and Shevchenko, P.V., 2021. Infection rate models for COVID-19: Model risk and public health news sentiment exposure adjustments. PLoS One, 16(6), p.e0253381.")
    st.write("Chalkiadakis IM. Statistical natural language processing and sentiment analysis with time-series: embeddings, modelling and applications. Heriot-Watt University, School of Engineering and Physical Sciences; 2022.")
    st.write("David Chavalarias, Paul Bouchaud, Victor Chomel, Maziyar Panahi. The new fronts of denialism and climate skepticism: Two years of Twitter exchanges under the macroscope. 2023. ⟨hal-04103183v2⟩")
    st.write("\n")
    st.write("\n")
    image1 = Image.open("{}/iscpif.png".format(base_path))
    st.image(image1, width=250)      
    image2 = Image.open("{}/nodes.png".format(base_path))
    st.image(image2, width=250)       
            

