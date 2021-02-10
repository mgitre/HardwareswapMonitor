import praw
import requests
import discord
import re
from discord import Webhook, RequestsWebhookAdapter, File

reddit_api_id = ""
reddit_api_secret = ""
user_agent="" #should take the form of "[any text, doesn't matter] u/Your_Username"

discord_webhook_id=""
discord_webhook_secret=""

reddit = praw.Reddit(client_id=reddit_api_id,client_secret=reddit_api_secret, user_agent=user_agent)
webhook = Webhook.partial(discord_webhook_id,discord_webhook_secret, adapter=RequestsWebhookAdapter())

discord_user_id = "" #your discord user ID - this is just so it can ping you when it's fairly certain it has detected a price, leave blank if you don't need it

keywords = [] #can't be anything that will be broken up by any of these characters: s,'/ +[]-
#this is case insensitive
#my config: ["RX580","580","RX570","570","RX480","480","RX470","470","RX590","590","5700","5700XT","RX5700","RX5700XT","1070","1080","1080ti","1070ti"]

def getPrice(string):
    if not "$" in string:
        return []
    matchDollarOrRange = r"\$\d+(?:\.\d+)?(?:(?:-| ?to ?)\$?\d+(?:\.\d+)?)?"
    matchShipped=matchDollarOrRange+r"\ ?shipped"
    matchPlusShipping=matchDollarOrRange+r"\ ?(?:\+|plus)\ ?ship(?:ping)?"
    matchAnything =matchDollarOrRange
    for reg in (matchShipped, matchPlusShipping, matchAnything):
        matches = re.findall(reg, string)
        if matches:
            return matches
    return []

def process(post):
    if post.link_flair_text=="BUYING":
        return
    keywords=["RX580","580","RX570","570","RX480","480","RX470","470","RX590","590","5700","5700XT","RX5700","RX5700XT","1070","1080","1080ti","1070ti"]
    delimiters="s|,|'|/| |\+|\[|\-"
    titlesplit = re.split(delimiters, post.title)

    selftextlower = post.selftext.lower()
    titlelower=post.title.lower()
    postsplit = re.split(delimiters, selftextlower)
    titlesplitbypart = re.split("\[(.*?)\]", titlelower)
    if len(titlesplitbypart)!=7:
        have=""
    else:
        have=titlesplitbypart[4]
    titlesplit = re.split(delimiters, have)
    for keyword in keywords:
        keyword = keyword.lower()
        if keyword in titlesplit:
            basetext="<@"+discord_user_id+">"
        else:
            basetext=" potentially "
        if keyword in postsplit or keyword in titlesplit:
            print(post.title)
            prices = getPrice(selftextlower)
            if len(prices)==1:
                print(keyword+basetext+"found at "+ " ".join(prices))
                webhook.send(keyword+basetext+"found at "+ " ".join(prices)+" "+post.url)
                
            elif len(prices)>=1:
                lines = [line for line in selftextlower.split("\n") if keyword in re.split(delimiters, line)]
                for line in lines:
                    prices = getPrice(line)
                    if len(prices)==0:
                        print(keyword+basetext+"found")
                        webhook.send(keyword+basetext+"found "+post.url)
                    elif len(prices)!=1:
                        print(keyword+basetext+"found, price could be: "+",".join(prices))
                        webhook.send(keyword+basetext+"found, price could be: "+",".join(prices)+" "+post.url)
                    else:
                        print(keyword+basetext+"found at "+prices[0])
                        webhook.send(keyword+basetext+"found at "+prices[0]+" "+post.url)
    

for submission in reddit.subreddit("hardwareswap").stream.submissions():
    process(submission)
