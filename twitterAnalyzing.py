import twitter
import json

apiKey = 'DelZY3GG8krnuMmXgmQOvCxnM'
apiSecretKey = 'Va73NeuAb7C69pavAPepzam7q5M2S26xW1BruNkpYFOGcdOjF8'
bearerToken = 'AAAAAAAAAAAAAAAAAAAAAI7%2BHQEAAAAAorzk67TC%2F%2FQJHrJ4XjD8w10BniI%3D9CtH9Vo0ejHvaz1m09CDN6ZuMmEDUmiOD7TAiaiKhrGqISMBRk'
auth = twitter.oauth2.OAuth2(apiKey,apiSecretKey,bearerToken)

twitter_api = twitter.Twitter(auth=auth)

WORLD_WOE_ID = 1

#使用https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-closest
#GET https://api.twitter.com/1.1/trends/closest.json?lat=37.781157&long=-122.400612831116(POSTMAN送)
#TW_WOE_ID = 23424971
LONDON_WOE_ID=44418
#https://www.findmecity.com/index.html
US_WOE_ID = 23424977

# Prefix ID with the underscore for query string parameterization.
# Without the underscore, the twitter package appends the ID value
# to the URL itself as a special case keyword argument.

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)

us_trends = twitter_api.trends.place(_id=US_WOE_ID)

for trend in world_trends[0]['trends']:
    print(trend['name'])
world_trends_set = set([trend['name'] 
                        for trend in world_trends[0]['trends']])

for trend in us_trends[0]['trends']:
    print(trend['name'])
us_trends_set = set([trend['name'] 
                     for trend in us_trends[0]['trends']]) 

common_trends = world_trends_set.intersection(us_trends_set)

q = '#MothersDay' 

count = 100

# Import unquote to prevent url encoding errors in next_results
from urllib.parse import unquote

# See https://dev.twitter.com/rest/reference/get/search/tweets

search_results = twitter_api.search.tweets(q=q, count=count)
#search_results中有statuses、search_metadata兩組資料，我們只要statues
#print(search_results)
#test=search_results['search_metadata']
#print(test)
statuses = search_results['statuses']

# Iterate through 5 more batches of results by following the cursor
for _ in range(5):
    print('Length of statuses', len(statuses))
    try:
        next_results = search_results['search_metadata']['next_results']
      #"search_metadata":{
      #"completed_in":0.053,
      #"max_id":1303244382229991425,
      #"max_id_str":"1303244382229991425",
      #"next_results":"?max_id=1303236275785342975&q=%23MothersDay&count=100&include_entities=1",
      #"query":"%23MothersDay",
      #"refresh_url":"?since_id=1303244382229991425&q=%23MothersDay&include_entities=1",
      #"count":10,
      #"since_id":0,
      #"since_id_str":"0"
      # }
    except KeyError as e: # No more results when next_results doesn't exist
        break
        
    # Create a dictionary from next_results, which has the following form:
    # next_results="?max_id=1303236275785342975&q=%23MothersDay&count=100&include_entities=1"
    
    kwargs = dict([ kv.split('=') for kv in unquote(next_results[1:]).split("&") ])
    print(kwargs)
    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

#dict convert to string ,second parameter is for reading
print(json.dumps(statuses[0], indent=1))


#前10個就好
for i in range(10):
    print()
    print(statuses[i]['text'])
    print('Favorites: ', statuses[i]['favorite_count'])
    print('Retweets: ', statuses[i]['retweet_count'])

#所有撈到的text
status_texts = [ status['text'] 
                 for status in statuses ]

screen_names = [ user_mention['screen_name'] 
                 for status in statuses
                     for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text'] 
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]

# Compute a collection of all words from all tweets
words = [ w 
          for t in status_texts 
              for w in t.split() ]

# Explore the first 5 items for each...
print(json.dumps(status_texts[0:5], indent=1))
print(json.dumps(screen_names[0:5], indent=1) )
print(json.dumps(hashtags[0:5], indent=1))
print(json.dumps(words[0:5], indent=1))

from collections import Counter
#統計一波
for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print(c.most_common()[:10]) # top 10
    print()

from prettytable import PrettyTable

for label, data in (('Word', words), 
                    ('Screen Name', screen_names), 
                    ('Hashtag', hashtags)):
    pt = PrettyTable(field_names=[label, 'Count']) 
    
    c = Counter(data)
    [ pt.add_row(kv) for kv in c.most_common()[:10] ]
    pt.align[label], pt.align['Count'] = 'l', 'r' # Set column alignment
    print(pt)

# A function for computing lexical diversity
def lexical_diversity(tokens):
    return len(set(tokens))/len(tokens) 

# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ]) 
    return total_words/len(statuses)

print(lexical_diversity(words))
print(lexical_diversity(screen_names))
print(lexical_diversity(hashtags))
print(average_words(status_texts))

retweets = [
            # Store out a tuple of these three values ...
            (status['retweet_count'], 
             status['retweeted_status']['user']['screen_name'],
             status['retweeted_status']['id'],
             status['text']) 
            
            # ... for each status ...
            for status in statuses 
            
            # ... so long as the status meets this condition.
                if 'retweeted_status' in status.keys()
           ]

# Slice off the first 5 from the sorted results and display each item in the tuple

pt = PrettyTable(field_names=['Count', 'Screen Name', 'Tweet ID', 'Text'])
[ pt.add_row(row) for row in sorted(retweets, reverse=True)[:5] ]
pt.max_width['Text'] = 50
pt.align= 'l'
print(pt)

_retweets = twitter_api.statuses.retweets(id=862359093398261760)

print([r['user']['screen_name'] for r in _retweets])

import matplotlib.pyplot as plt

#一種魔法函數 用來內崁繪圖，也可以直接省略plt.show()
#%matplotlib inline
word_counts = sorted(Counter(words).values(), reverse=True)

plt.loglog(word_counts)
plt.ylabel("Freq")
plt.xlabel("Word Rank")
plt.figure()


for label, data in (('Words', words), 
                    ('Screen Names', screen_names), 
                    ('Hashtags', hashtags)):

    # Build a frequency map for each set of data
    # and plot the values
    c = Counter(data)
    plt.hist(list(c.values()))
    
    # Add a title and y-label ...
    plt.title(label)
    plt.ylabel("Number of items in bin")
    plt.xlabel("Bins (number of times an item appeared)")
    
    # ... and display as a new figure
    plt.figure()


counts = [count for count, _, _, _ in retweets]

plt.hist(counts)
plt.title('Retweets')
plt.xlabel('Bins (number of times retweeted)')
plt.ylabel('Number of tweets in bin')
plt.show()