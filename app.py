import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import emoji

st.sidebar.title("whatsapp chat analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocessor(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"overall")

    selected_user = st.sidebar.selectbox("show analysis wrt",user_list)

    if st.sidebar.button("show analysis"):
        #stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)

        st.title('Top Statistics 🔝')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("total messages")
            st.title(num_messages)
        with col2:
            st.header("total words")
            st.title(words)
        with col3:
            st.header("media shared")
            st.title(num_media_messages)
        with col4:
            st.header("links shared")
            st.title(num_links)

        #monthly timeline
        st.title('monthly timeline 🈷️')
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #daily timeline
        st.title('daily timeline 🈷')
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity map 🗺️')
        col1,col2 = st.columns(2)

        with col1:
            st.header('Most busy day')
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header('Most busy month')
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # FIX 2: pass ax into heatmap instead of overwriting it
        st.title('Weekly Activity Map 🤸')
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        #finding the busiest users in the group(group level)
        if selected_user == 'overall':
            st.title('most busy users 😉')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            # FIX 3: removed extra trailing comma
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Word cloud 😎")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is None:
            st.warning("Not enough words to generate a word cloud for this user.")
        else:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

        # FIX 4: added empty check before plotting most common words
        st.title('most common words 🙊')
        most_common_df = helper.most_common_words(selected_user, df)
        if most_common_df.empty:
            st.warning("No common words found for this user.")
        else:
            fig,ax = plt.subplots()
            ax.barh(most_common_df[0],most_common_df[1])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title('emoji analysis')

        col1,col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)

        with col2:
            if emoji_df.empty or len(emoji_df) == 0:
                st.warning("No emoji data found for this user.")
            else:
                fig, ax = plt.subplots()
                labels = emoji_df.iloc[:, 0].head().apply(lambda x: emoji.demojize(x))
                ax.pie(
                    emoji_df.iloc[:, 1].head(),
                    labels=labels,
                    autopct='%0.2f'
                )
                st.pyplot(fig)