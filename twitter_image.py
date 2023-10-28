import os
import requests
import tweepy

# 设置socks5代理环境变量
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:7890'

# 定义你的API凭据
consumer_key = 'gl5gBMwPz614uqT8qeDShj5zz'
consumer_secret = 'VJflaybP4tTiy2XFuwwG578Z8IYqsCmOhiNZu0uQ8VpF4XEFbB'
access_token = '1070311404790603776-K0WlVjvxY7aV4gB7vZqOWLP1QaXq23'
access_token_secret = 'Jk28nj0Rq68eFs3WCAHYoOfNZmUK42lALWYHhMwWIsvIp'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEGeqgEAAAAAUZ%2B5JxPYT96C7DzjMEEPrT%2FjjGg%3D64yghGuWqrZvTJ1mMsUZDY8LKCFF0vCgtuHY3ZjAzXNcQMEIij"


client = tweepy.Client(bearer_token)

# Get Tweets

# This endpoint/method returns a variety of information about the Tweet(s)
# specified by the requested ID or list of IDs

tweet_ids = [1460323737035677698, 1293593516040269825, 1293595870563381249]

# By default, only the ID and text fields of each Tweet will be returned
# Additional fields can be retrieved using the tweet_fields parameter
response = client.get_tweets(tweet_ids, tweet_fields=["created_at"])

for tweet in response.data:
    print(tweet.id, tweet.created_at)