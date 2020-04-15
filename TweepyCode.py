
import tweepy
#sys.path
#sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def main():
  # Fill in the values noted in previous step here
  cfg = { 
    "consumer_key"        : "x",
    "consumer_secret"     : "x",
    "access_token"        : "x",
    "access_token_secret" : "x" 
    }

  api = get_api(cfg)
  tweet = "Hello, world!"
  status = api.update_status(status=tweet) 
  # Yes, tweet is called 'status' rather confusing

if __name__ == "__main__":
  main()
