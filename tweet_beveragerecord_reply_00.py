import os
import tweepy
import datetime
import pandas as pd
import numpy as np
import random
import re


# 各種キーを入れる
CONSUMER_KEY = os.environ['CONSUMER_KEY'] 
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)
    

# 自分宛てのメンション(50件)の時刻(UTC)、ユーザID、内容を取得
for mentions in tweepy.Cursor(api.mentions_timeline).items(50):
    mention_time = mentions.created_at
    user_name = mentions.user.name
    user_ID = mentions.user.screen_name
    tweet_ID = mentions.id
    mention_content = mentions.text

    # ツイートの元となるリストを生成
    ## CSVファイルのリストから抽出
    df = pd.read_csv('drinklist.csv', \
                     names = ['title', 'star', \
                              'remark', 'link', 'created_at', \
                              'ltd_sale', \
                              'flvr1', 'flvr2'])

    ds = df.sample()

    ext_row = ds.values.tolist()
    data = ext_row[0]

    drink_name = data[0]
    drink_remark = data[2]
    drink_link = data[3]

    # メンションが今より10分前以内ならツイートする。それより過去なら何もしない。
    now = datetime.datetime.now()
    ref_time = now - datetime.timedelta(minutes=10)
    if ref_time <= mention_time:
        
        # ①フレーバー指定
        df2 = pd.read_csv('flavorlist.csv',
                          names = ['ID', 'kwd0', 'kwd1', 'kwd2', 'kwd3'])

        df3 = df2.drop('ID', axis = 1)
        df4 = df3.fillna('XXXX')

        kwds_list = df4.values.flatten() # DataFrameを単一のListに変換
        kwds = '|'.join(kwds_list) # 境界を|としてListをStrに変換（正規表現検索のため）

        if re.search(kwds, mention_content):
            match = re.findall(kwds, mention_content)[0] # マッチするフレーバーを検出（最初の1つ）
            r_bool = df2.isin([match])
            match_row = r_bool[(r_bool.kwd0 == True) | \
                             (r_bool.kwd1 == True) | \
                             (r_bool.kwd2 == True) | \
                             (r_bool.kwd3 == True)] # フレーバーがマッチする行を取得
            matchID = match_row.index.values # 行番号を取得(List)

    
            flvrID = [] # 該当するフレーバー番号を抽出
            for i in matchID:
                item = df2['ID'].loc[i]
                flvrID.append(item)
            
            #フレーバー番号にマッチするジュースを抽出しておすすめ候補リスト作成
            try:
                cand_list_orig = []
                for j in flvrID:
                    cand = df[(df.flvr1 == j) | (df.flvr2 == j)]
                    cand_row = cand.index.values
                    for k in cand_row:
                        cand_element = cand.loc[:, ['title', 'remark', 'link']]
                        cand_list_orig.append(cand_element.values.tolist()[0])
            
                # 候補リストの重複を削除
                cand_set = set(list(map(tuple, cand_list_orig))) 
                cand_list = list(cand_set)

                cand_sample = random.choice(cand_list)

                drink_name_f = cand_sample[0]
                drink_remark_f = cand_sample[1]
                drink_link_f = cand_sample[2]

                tweet_content = '@' + user_ID + ' ' \
                                + user_name + 'さんへのおすすめ' \
                                + match + 'フレーバーは' \
                                + '「' + drink_name_f + '」です！' \
                                + drink_link_f

            except IndexError:
                tweet_content = '@' + user_ID + ' ' \
                                + 'ごめんなさい！' \
                                + match + 'フレーバーのジュースはまだ登録されていません！' \
                                + 'おすすめのジュースがあればDMで教えてください～'

        # ②おすすめ 
        elif re.search('勧め|すすめ|ススメ', mention_content):            
            tweet_content = '@' + user_ID + ' ' \
                            + user_name + 'さんへのおすすめは' \
                            + '「' + drink_name + '」です！\n' \
                            + drink_remark + '\n' \
                            + drink_link

        # ③労働    
        elif re.search('働き|はたらき|労働|テスト', mention_content):
            labor_list = ['働きたくないね', '働きたくないよ～', '働きたくない！']
            tweet_content = '@' + user_ID + ' ' \
                            + random.choice(labor_list) + '\n' \
                            + 'ジュース飲んで忘れよう！' \
                            + drink_link

        # ④酒
        elif re.search('酒|ビール', mention_content):
            tweet_content = '@' + user_ID + ' ' \
                            + 'ジュース飲もうね'

        # あいさつ
        elif re.search('ありがとう', mention_content):
            tweet_content = '@' + user_ID + ' ' \
                            + 'どういたしまして！'
        # あいさつ2
        elif re.search('楽しい|たのしい|嬉しい|うれしい|面白い|おもしろい|すごい', mention_content):
            tweet_content = '@' + user_ID + ' ' \
                            + 'ありがとうございます！'
        
            
        # その他    
        else:
            tweet_content = '@' + user_ID + ' ' \
                            + '「おすすめ」や好きなフレーバーを含んで返信してみてください♪'

        
        print(tweet_content)
        api.update_status(tweet_content, in_reply_to_status_id = tweet_ID)
        
    else:
        pass
