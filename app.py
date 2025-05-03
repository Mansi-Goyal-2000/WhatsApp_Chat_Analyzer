import streamlit as st
import preprocessor
import helper
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import matplotlib.pyplot as plt

PRIMARY_COLOR = "#1E88E5"         # Primary accent color
TEXT_COLOR = "#F5F5F5"            # Text color
BACKGROUND_COLOR = "#121212"      # Main background color
SECONDARY_BG_COLOR = "#1E1E1E"

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
        :root {
            --primary-color: """ + PRIMARY_COLOR + """;
            --background-color: """ + BACKGROUND_COLOR + """;
            --secondary-background-color: """ + SECONDARY_BG_COLOR + """;
            --text-color: """ + TEXT_COLOR + """;
            --font: sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("WhatsApp Chat Analyzer")

# Uploading WhatsApp chat file
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file", type=["txt"])

if uploaded_file is not None:
    # Read the file
    bytes_data = uploaded_file.getvalue()
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        # Try with a different encoding if utf-8 fails
        data = bytes_data.decode("latin-1")

    # Preprocess the data
    df = preprocessor.preprocess(data)

    # Fetch all unique users
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show Analysis"):
        st.title(f"WhatsApp Chat Analysis: {selected_user if selected_user != 'Overall' else 'All Users'}")

        # Fetch statistics
        num_messages, words, num_media, num_links = helper.fetch_stats(selected_user, df)

        # Display key metrics
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media)
        with col4:
            st.metric("Links Shared", num_links)

        # Monthly Timeline
        st.subheader("Monthly Activity")
        timeline = helper.monthly_timeline(selected_user, df)
        fig = px.line(timeline, x='time', y='message',
                      title="Messages per Month",
                      labels={'message': 'Number of Messages', 'time': 'Month'},
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Daily Timeline
        st.subheader("Daily Activity")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig = px.line(daily_timeline, x='only_date', y='message',
                      title="Messages per Day",
                      labels={'message': 'Number of Messages', 'only_date': 'Date'},
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Activity Map
        st.subheader("Activity Patterns")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Most Active Day of Week**")
            busy_day = helper.week_activity_map(selected_user, df)

            # Convert Series to DataFrame for Plotly
            busy_day_df = busy_day.reset_index()
            busy_day_df.columns = ['Day', 'Messages']

            fig = px.bar(
                busy_day_df,
                x='Day',
                y='Messages',
                title="Messages by Day of Week"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Most Active Month**")
            busy_month = helper.month_activity_map(selected_user, df)

            # Convert Series to DataFrame for Plotly
            busy_month_df = busy_month.reset_index()
            busy_month_df.columns = ['Month', 'Messages']

            fig = px.bar(
                busy_month_df,
                x='Month',
                y='Messages',
                title="Messages by Month"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Weekly Activity Heatmap
        st.subheader("Activity Heatmap")

        # Generate and display heatmap
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)
        # Most Active Users (only for Overall)
        if selected_user == "Overall":
            st.subheader("Most Active Users")
            col1, col2 = st.columns(2)

            x, new_df = helper.most_active_user(df)

            with col1:
                # Convert Series to DataFrame for Plotly
                active_users_df = x.reset_index()
                active_users_df.columns = ['User', 'Messages']

                fig = px.bar(
                    active_users_df,
                    x='User',
                    y='Messages',
                    title="Message Count by User"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**Percentage Contribution**")
                st.dataframe(new_df, use_container_width=True)

        # Wordcloud
        st.subheader("Word Cloud")
        try:
            wc = helper.create_word_cloud(selected_user, df)
            # Convert WordCloud to Plotly figure
            layout = wc.layout_
            fig = go.Figure()

            for (word, count), font_size, position, orientation, color in layout:
                x, y = position
                xi = x / wc.width
                yi = 1 - (y / wc.height)

                fig.add_trace(go.Scatter(
                    x=[xi], y=[yi],
                    text=[word],
                    mode="text",
                    textfont=dict(
                        size=font_size,
                        color=color
                    ),
                    hovertemplate=f"{word}: {count}<extra></extra>"
                ))

            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor="black",
                plot_bgcolor="black",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating word cloud: {e}")
            st.info("Try with a different user or dataset with more text content.")

        # Emoji Analysis
        st.subheader("Emoji Analysis")
        try:
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Top Emojis**")
                    emoji_df.columns = ['Emoji', 'Count']
                    st.dataframe(emoji_df, use_container_width=True)

                with col2:
                    if len(emoji_df) > 0:
                        fig = px.pie(emoji_df, values='Count', names='Emoji', title="Emoji Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No emojis found in the selected messages.")
            else:
                st.info("No emojis found in the selected messages.")
        except Exception as e:
            st.error(f"Error analyzing emojis: {e}")
else:
    st.subheader("Get Started")

    st.info("""
    📄 To begin, export any WhatsApp chat file in `.txt` format and upload it using the sidebar.

    ⚠️ Your data is processed locally and is **not stored** anywhere.

    👉 Steps to export a chat from WhatsApp:
    1. Open the chat in WhatsApp.
    2. Tap on the chat name at the top.
    3. Select **Export Chat**.
    4. Choose to export **Without Media**.
    5. Save the file as `.txt` and upload it in the sidebar.
    """)

# import streamlit as st
# import preprocessor
# import helper
# import plotly.express as px
# import plotly.graph_objects as go
#
# # Page configuration for wide layout
# st.set_page_config(
#     page_title="WhatsApp Chat Analyzer",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
#
# st.sidebar.title("WhatsApp Chat Analyzer")
#
# if "analysis_started" not in st.session_state:
#     st.session_state.analysis_started = False
#
#
# if not st.session_state.analysis_started:
#     st.subheader("Get Started")
#
#     st.info("""
#     📄 To begin, export any WhatsApp chat file in `.txt` format and upload it here.
#
#     ⚠️ Your data is processed locally and is **not stored** anywhere.
#
#     👉 Steps to export a chat from WhatsApp:
#     1. Open the chat in WhatsApp.
#     2. Tap on the chat name at the top.
#     3. Select **Export Chat**.
#     4. Choose to export **Without Media**.
#     5. Save the file as `.txt` and upload it in the sidebar clicking 'Browse files'.
#     """)
#
# #     # File uploader
# #     uploaded_file = st.file_uploader("Upload a WhatsApp chat file", type=["txt"])
# #
# #     # Process the uploaded file
# #     if uploaded_file is not None:
# #         bytes_data = uploaded_file.getvalue()
# #         data = bytes_data.decode("utf-8")
# #         df = preprocessor.preprocess(data)
# #         st.session_state.analysis_started = True
# # else:
# #     st.subheader("Analysis in Progress")
# #     # Perform analysis using `df`
# #     if st.button("Restart"):
# #         st.session_state.analysis_started = False
# #
# # # Place your analysis logic below...
# # if st.session_state.analysis_started:
# #     # Your analysis and chart rendering logic
# #     st.write("Displaying analysis...")
#
# # Uploading WhatsApp chat file
# uploaded_file = st.sidebar.file_uploader("Choose a file")
# if uploaded_file is not None:
#     bytes_data = uploaded_file.getvalue()
#     data = bytes_data.decode("utf-8")
#     df = preprocessor.preprocess(data)
#
#     # Fetch all unique users
#     user_list = df['user'].unique().tolist()
#     user_list.sort()
#     user_list.insert(0, "Overall")
#
#     selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)
#
#     if st.sidebar.button("Show Analysis"):
#         # Fetch statistics
#         num_messages, words, num_media, num_links = helper.fetch_stats(selected_user, df)
#         st.title("Top Statistics")
#         col1, col2, col3, col4 = st.columns(4)
#
#         col1.metric("Total Messages", num_messages)
#         col2.metric("Total Words", words)
#         col3.metric("Media Shared", num_media)
#         col4.metric("Links Shared", num_links)
#
#         # Monthly Timeline
#         st.title("Monthly Timeline")
#         timeline = helper.monthly_timeline(selected_user, df)
#         fig = px.line(timeline, x='time', y='message', title="Monthly Timeline", markers=True)
#         st.plotly_chart(fig, use_container_width=True)
#
#         # Daily Timeline
#         st.title("Daily Timeline")
#         daily_timeline = helper.daily_timeline(selected_user, df)
#         fig = px.line(daily_timeline, x='only_date', y='message', title="Daily Timeline", markers=True)
#         st.plotly_chart(fig, use_container_width=True)
#
#         # Activity Map
#         st.title("Activity Map")
#         col1, col2 = st.columns(2)
#
#         with col1:
#             st.header("Most Busy Day")
#             busy_day = helper.week_activity_map(selected_user, df)
#             fig = px.bar(busy_day, x=busy_day.index, y=busy_day.values, title="Most Busy Day")
#             st.plotly_chart(fig, use_container_width=True)
#
#         with col2:
#             st.header("Most Busy Month")
#             busy_month = helper.month_activity_map(selected_user, df)
#             fig = px.bar(busy_month, x=busy_month.index, y=busy_month.values, title="Most Busy Month")
#             st.plotly_chart(fig, use_container_width=True)
#
#         # Weekly Activity Heatmap
#         st.title("Weekly Activity Map")
#         fig = helper.activity_heatmap(selected_user, df)
#         st.plotly_chart(fig, use_container_width=True)
#         user_heatmap = helper.activity_heatmap(selected_user, df)
#         fig, ax = plt.subplots()
#         ax = sns.heatmap(user_heatmap)
#         st.pyplot(fig)

#         # Most Active Users
#         if selected_user == "Overall":
#             st.title("Most Active Users")
#             x, new_df = helper.most_active_user(df)
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 fig = px.bar(x, x=x.index, y=x.values, labels={'x': 'Users', 'y': 'Messages'}, title="Most Active Users")
#                 st.plotly_chart(fig, use_container_width=True)
#
#             with col2:
#                 st.dataframe(new_df)
#
#         # Wordcloud
#         st.title("Wordcloud")
#         df_wc = helper.create_word_cloud(selected_user, df)
#         layout = df_wc.layout_
#         fig = go.Figure()
#
#         for (word, count), font_size, position, orientation, color in layout:
#             x, y = position
#             xi = x / df_wc.width
#             yi = 1 - (y / df_wc.height)
#
#             fig.add_trace(go.Scatter(
#                 x=[xi], y=[yi],
#                 text=[word],
#                 mode="text",
#                 textfont=dict(
#                     size=font_size,
#                     color=color
#                 ),
#                 hovertemplate=f"{word}: {count}<extra></extra>"
#             ))
#
#         fig.update_layout(
#             xaxis=dict(showgrid=False, zeroline=False, visible=False),
#             yaxis=dict(showgrid=False, zeroline=False, visible=False),
#             margin=dict(l=0, r=0, t=40, b=0),
#             paper_bgcolor="black",
#             plot_bgcolor="black",
#             height=400
#         )
#         st.plotly_chart(fig, use_container_width=True)
#
#         # Emoji Analysis
#         st.title("Emoji Analysis")
#         emoji_df = helper.emoji_helper(selected_user, df)
#         col1, col2 = st.columns(2)
#
#         with col1:
#             st.dataframe(emoji_df)
#
#         with col2:
#             fig = px.pie(emoji_df, values=1, names=0)
#             st.plotly_chart(fig, use_container_width=True)
