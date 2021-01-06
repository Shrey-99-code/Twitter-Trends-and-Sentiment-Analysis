import tweepy
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

import numpy as np
import matplotlib.pyplot as plt
import re
from textblob import TextBlob

#---------------------------------------------------------------------------------------------------------------------------------
# Authentication
#---------------------------------------------------------------------------------------------------------------------------------
consumer_key = # Enter Consumer Key
consumer_key_secret = # Enter Consumer Key Secret

access_token = # Enter Access Key
access_token_secret = # Enter Access Key Secret

def authenticate(consumer_key, consumer_key_secret, access_token, access_token_secret):
	auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True)
	return api

api = authenticate(consumer_key, consumer_key_secret, access_token, access_token_secret)

#---------------------------------------------------------------------------------------------------------------------------------
# Finding tweets on the basis of a Twitter Account
#---------------------------------------------------------------------------------------------------------------------------------

def get_user_specific_tweets(user, max_tweets):
	tweets = api.user_timeline(screen_name = user, count = max_tweets)
	return tweets
#---------------------------------------------------------------------------------------------------------------------------------
# Creating a DataFrame on the basis of a Twitter Account's tweets
#---------------------------------------------------------------------------------------------------------------------------------

def create_user_df(tweets):
	tweet_lst, date_lst, like_lst, retweet_lst = [],[],[],[]
	for tweet in tweets:
		tweet_lst.append(tweet.text)
		date_lst.append(tweet.created_at)
		like_lst.append(tweet.favorite_count)
		retweet_lst.append(tweet.retweet_count)

	data = {"Date" : date_lst, "Tweets" : tweet_lst, "Likes" : like_lst, "Retweets" : retweet_lst}
	df = pd.DataFrame(data)
	df.index = np.arange(1, len(df) + 1)
	return df

#---------------------------------------------------------------------------------------------------------------------------------
# Creating a DataFrame on the basis of Key-words provided
#---------------------------------------------------------------------------------------------------------------------------------

def create_df(query, max_tweets):
	searched_tweets = [status for status in tweepy.Cursor(api.search, q=query, lang = 'en').items(max_tweets)]
	tweet_lst, date_lst, like_lst, retweet_lst = [],[],[],[]
	for tweet in searched_tweets:
		tweet_lst.append(tweet.text)
		date_lst.append(tweet.created_at)
		like_lst.append(tweet.favorite_count)
		retweet_lst.append(tweet.retweet_count)

	data = {"Date" : date_lst, "Tweets" : tweet_lst, "Likes" : like_lst, "Retweets" : retweet_lst}
	df = pd.DataFrame(data)
	df.index = np.arange(1, len(df) + 1)
	return df


#---------------------------------------------------------------------------------------------------------------------------------
# Creating a two plots:
# 1) First plot compares the number of likes, and retweets of the given tweets, in relation to the dates they were posted on
# 2) Second plot compares the 
#---------------------------------------------------------------------------------------------------------------------------------

def graph_df(df,user):

	# myInt = (np.mean(df['Retweets']) * 2)
	# size = [num / myInt for num in df['Retweets']]

	# plt.scatter(df['Date'], df['Likes'], c = 'r', s = size)
	# # plt.scatter(df['Date'], df['Retweets'], c = 'b')

	like_plot = pd.Series(data = df['Likes'].values, index = df['Date'])
	like_plot.plot(figsize = (16,4), color = 'r')
	rt_plot = pd.Series(data = df['Retweets'].values, index = df['Date'])
	rt_plot.plot(figsize = (16,4), color = 'b')

	plt.legend(['Likes', 'Retweets', 'Average Likes'])
	plt.title(user + ": Tweet Likes and Retweets Plot")
	
	plt.xlabel('Date')
	plt.ylabel('Impressions')

	plt.show()

def graph_df_sent(df, user= None):
	sent_plot = pd.Series(data = df['Sentiment'].values, index = df['Date'])
	sent_plot.plot(figsize = (16,4), color = 'g')

	subj_plot = pd.Series(data = df['Subjectivity'].values, index = df['Date'])
	subj_plot.plot(figsize = (16,4), color = 'y')

	plt.plot(df['Date'], my_mean(df, 'Sentiment'), color = 'b')
	plt.plot(df['Date'], my_mean(df, 'Subjectivity'), color = 'r')

	plt.legend(['Sentiment', 'Subjectivity', 'Average Sentiment', 'Average Subjectivity'])
	plt.title(user + ": Sentiment and Subjectivity Plot")
	plt.xlabel('Date')
	plt.ylabel('Range')

	plt.show()

def add_sentiment(df):
	sentiment_lst = []
	subjectivity_lst = []
	for tweet in df['Tweets']:
		sentiment_lst.append((clean_and_analyze_tweet(tweet)).polarity)
		subjectivity_lst.append((clean_and_analyze_tweet(tweet)).subjectivity)

	df['Sentiment'] = sentiment_lst
	df['Subjectivity'] = subjectivity_lst
	return df

def clean_and_analyze_tweet(tweet):
	cleaned_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
	analysis = TextBlob(cleaned_tweet)
	return analysis.sentiment

def stdout(df, user):
	print(df)
	graph_df(df, user)
	graph_df_sent(df, user)

def my_mean(df, col_name):
	avg = np.mean(df[col_name])
	factor = len(df[col_name])

	return ([avg] * factor)


def filter_df_by_date(df, start_date, end_date):
	start_index = df[df['Date'] == start_date].index[0]
	end_index = df[df['Date'] == end_date].index[0]

	new_df = df.iloc[start_index: (end_index + 1)]
	return new_df

def main():
	while True:
		print('Enter Q to quit the program anytime')
		choice = str(input('Would you like to analyze a Twitter account (Enter T), or specific keywords (Enter K)? '))

		if choice == 'T':
			user = str(input('Enter Twitter username: '))
			if user == 'Q':
				print()
				exit()
			elif len(user.split()) == 1:
				num_tweets = int(input('Enter Number of Tweets for Analysis (max 200): '))
				if num_tweets == 'Q':
					print()
					exit()

				user_tweets = get_user_specific_tweets(user, num_tweets)
				user_df = add_sentiment(create_user_df(user_tweets))
				stdout(user_df, user)

				filter_choice = input('Enter F to filter the data further, otherwise enter anything else: ')

				if filter_choice == 'F':
					
					start_date = input('Enter starting date: ')
					end_date = input('Enter ending date: ')
					stdout((filter_df_by_date(user_df, end_date, start_date)), user)
					main()
				
				else:
					main()

			else:
				print('Invalid Input \n ')
				main()

		elif choice == 'K':
			query = str(input('Enter keywords seperated by space: '))
			if query == 'Q':
				print()
				exit()
			elif len(query.split()) == 0:
				print('Invalid Input \n ')
				main()
			else:
				query = query.split()
				num_tweets = int(input('Enter Number of Tweets for Analysis (max 200): '))
				if num_tweets == 'Q':
					print()
					exit()
				query_df = add_sentiment(create_df(query, num_tweets))				
				keys_str = ""

				for key in query:
					keys_str += (key + " ")

				stdout(query_df, keys_str)

				filter_choice = input('Enter F to filter the data further, otherwise enter anything else: ')

				if filter_choice == 'F':
					
					start_date = input('Enter starting date: ')
					end_date = input('Enter ending date: ')
					stdout((filter_df_by_date(query_df, end_date, start_date)), keys_str)
					main()
				
				else:
					main()

		elif choice == 'Q':
			print()
			exit()
		else:
			print('Invalid Input \n ')
			main()


main()





        
