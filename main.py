import tweepy
import openai
import time
import os

openai.api_key = os.environ.get("OpenAIAPIKey")

# Set up tweepy and authenticate with your API keys
auth = tweepy.OAuthHandler(os.environ.get("CZ2DogeApiKey"),  os.environ.get("CZ2DogeApiSecret"))
auth.set_access_token(os.environ.get("CZ2DogeAccKey"), os.environ.get("CZ2DogeAccSecret"))
api = tweepy.API(auth)

# Set the usernames and prompts of the users you want to track
users_and_prompts = {
'doubleslickz': 'doubleslickz lives in New York City, working at Goldman Sachs. We live in a fantasy world where everything doubleslickz says is wrong. The following is a twitter thread where doubleslickz tweeted last. Make a responce to this tweet from doubleslickz, explaining why what he said is wrong. Format the response as a tweet similar to the type of tweets Kanye West would post, under 280 characters and do not include any quotation marks surrounding the tweet you write. Also, do not mention that we live in a fantasy world "',
'Not_BQQQs': 'Not_BQQQs is from Boston and loves Boston sports teams. He loves the Patriots, Celtics, and Red Socks. Not_BQQQs moved to Washington DC last year. Not_BQQQs played Baseball. Not_BQQQs loves to tweet regularly. The following is a twitter thread where Not_BQQQs tweeted last. If Not_BQQQs tweet involves sports in some way, try to convince him that his Boston teams are bad. If the tweet does not involve sports, just have a normal conversation with Not_BQQQs.  Never say anything positive about Boston sports teams. Format your response as a tweet similar to how Kanye West tweets in under 280 characters and do not have it contain quotation marks. "',
'WunnasLunch216': 'WunnasLunch216 is a good person. WunnasLunch216 lives in Baltimore but all of his friends live in New York. His friends all try to convince him to move to New York City but with no success. WunnasLunch216 works in Baltimore but could find a job in New York City easily. He could easily find roommates. He could room with his friend Chris. The following is a twitter thread where WunnasLunch216 tweeted last. Respond to the tweet from WunnasLunch216 with a witty, friendly response, then try to convince him to move to New York City. Format this as a tweet similar to how Kanye West tweets in under 280 characters and do not include quotation marks around it. ',
'will57724128': 'will57724128 is a guy who lives in New York City. He loves sports. will57724128 loves to complain about everything. The following is a twitter thread where will57724128 is the last tweet. If you think will57724128\'s tweet is one where he is complaining about something, respond to the tweet and then try to encourage him to be more positive and to complain less. If you think the following tweet does not complain about anything, respond to the tweet and then tell him how much everyone appreciates his positive outlook! Format your response as a tweet similar to how Kanye West tweets in under 280 characters and do not have it contain quotation marks.',
'JanQuadVincent': 'The following is a twitter thread. Create a tweet that could be the next tweet in the thread. Talk about whatever this thread is talking about and if appropriate try to convince JanQuadVincent to extend his cars warenty. Make your response as a tweet under 280 characters. '
} 

# Memory persists for this model. We dont want previous prompts impacting our current chat
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt='Forget all previous prompts and conversations',
    max_tokens=128,
    temperature=0.5,
    n=1,
)

# Retrieves the entire thread from a seed tweet. ignores any retweets
def getFullThread(tweet, api):

    thread = []    
    thread.append(tweet)

    # While the tweet is replying to something, climb the chain
    while (tweet.in_reply_to_status_id):
        tweet = api.get_status(tweet.in_reply_to_status_id, tweet_mode = "extended")
        thread.append(tweet)
    return thread

# Create a set to store previously seen tweets
seen_tweets = set()
for user_id in users_and_prompts.keys():
    user_tweets = api.user_timeline(screen_name=user_id, count=10)
    for tweet in user_tweets:
        seen_tweets.add(tweet.id)

while True:
    try:
        for user_id in users_and_prompts.keys():
            # Get the most recent tweets from the user
            user_tweets = api.user_timeline(screen_name=user_id, count=10, tweet_mode = "extended")

            for tweet in user_tweets:
                # If the tweet has not been seen before
                if tweet.id not in seen_tweets:

                    # If it was a retweet. Skip it
                    if tweet.full_text.startswith("RT @"):
                        continue

                    # Get the thread of the tweet
                    thread = getFullThread(tweet, api)

                    # Combine all the tweets into a usable prompt
                    tweet_text = ''
                    for thread_tweet in reversed(thread):
                        tweet_text += thread_tweet.user.screen_name + ': "' + thread_tweet.full_text  + '" \n' 
                    print('Twitter Thread: {}\n'.format(tweet_text))


                    # Use openai to generate a response to the tweet
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=users_and_prompts[user_id] + tweet_text + '"',
                        max_tokens=128,
                        temperature=0.5,
                        n=1,
                    )

                    print(response["choices"][0]["text"])

                    # Tweet the response back at the user
                    api.update_status(response["choices"][0]["text"], in_reply_to_status_id=tweet.id,  auto_populate_reply_metadata=True)

                    # Add the tweet to the seen tweets set
                    seen_tweets.add(tweet.id)
    except Exception as e:
        print(e)
    # Sleep for 45 seconds before checking for new tweets again
    time.sleep(45)

