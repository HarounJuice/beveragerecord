import pandas as pd
import numpy
import tweepy
import os

# CSVファイルのリストから1行をランダム抽出
df = pd.read_csv('drinklist.csv', encoding='cp932')
ds = df.sample()

# 抽出した行をDataFrame型からList型に変換
ext_row = ds.values.tolist()
data = ext_row[0]

# Twitter投稿用の文を作る
drink_name = data[1]
drink_star = '★' * data[2]
drink_remark = data[3]
drink_link = data[4]
    
tweet_content = '「' + drink_name + '」\n' \
                + '・お気に入り度：' + drink_star + '\n' \
                + '・コメント：' + '\n' \
                + drink_remark + '\n' \
                + drink_link

# 各種キーを入れる
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

#APIインスタンスを作成
api = tweepy.API(auth)

# ツイートする
api.update_status(tweet_content)


