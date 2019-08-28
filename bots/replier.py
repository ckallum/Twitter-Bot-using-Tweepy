import tweepy
import json
import logging

SCRIPTED_MSG = "Thanks for messaging KE-BOT, Message courtesy of KE-BOT"


class TweetListener(tweepy.StreamListener):
    def __init__(self, users, api):
        super().__init__()
        self.tracking = [user["id"] for user in users]
        self.user = api.me()
        self.api = api

    def on_connect(self):
        print("Bot connected, tracking {}".format([user["handle"] for user in self.tracking]))

    def on_status(self, status):
        if status.user.id_str in self.tracking:
            if not status.user.following:
                self.user.follow(status.user.id_str)
            print("Tweeted at {}".format(status.user.id_str))
            self.api.update_status("@{} {}".format(status.user.id_str, SCRIPTED_MSG))



def get_bot():
    with open("json/bot.json", "r") as auth:
        bot_data = json.load(auth)
        return bot_data


def get_users():
    with open("json/users.json", "r") as users:
        users = json.load(users)
        return users


def create_api(bot_auth):
    logger = logging.getLogger()
    auth = tweepy.OAuthHandler(bot_auth["consumer_key"], bot_auth["consumer_secret"])
    auth.access_token = bot_auth["access_token"]
    auth.access_token_secret = bot_auth["access_token_secret"]
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API")
        raise e
    logger.info("API created")
    return api


def start_process(users, bot_auth):
    api = create_api(bot_auth)
    listener = TweetListener(users, api)
    while True:
        stream = tweepy.Stream(api.auth, listener)
        stream.filter(track="@{}".format(bot_auth["handle"]), is_async=True, follow=users)


def main():
    users = get_users()
    bot_auth = get_bot()
    if not users:
        print("No users given")
    if not bot_auth:
        print("No bot given")

    start_process(users, bot_auth)


if __name__ == '__main__':
    main()
