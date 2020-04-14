
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
    "consumer_key"        : "fuuAgy3pElOz4Ecy4ZF1OSuRh",
    "consumer_secret"     : "7XZnEh5PwXHQ2AH8Ma52g41aAB0D2cTvDSbPaHnzErPSzDAnZt",
    "access_token"        : "1247287333478699008-KKpYUUHBBxDpJwudh525izgb1EZOVF",
    "access_token_secret" : "ZDNOfmy2iV9dGNEce14Bgqym2g4j2cEhpibGaztv9GxVc" 
    }

  api = get_api(cfg)
  tweet = "Hello, world!"
  status = api.update_status(status=tweet) 
  # Yes, tweet is called 'status' rather confusing

if __name__ == "__main__":
  main()