import time
from datetime import datetime, date

class FeedingProfile:
    def __init__(self, user_id, portion_grams, feed_times, days, start_date, end_date):
        self.user_id = user_id
        self.portion_grams = portion_grams
        self.feed_times = feed_times
        self.days = days
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    def is_active_now(self):
        now = datetime.now()
        today = now.date()
        current_time = now.strftime('%H:%M')
        weekday = now.strftime('%A')

        if not (self.start_date <= today <= self.end_date):
            return False

        if self.days != "daily" and weekday not in self.days:
            return False

        return current_time in self.feed_times

    def __repr__(self):
        return f"<FeedingProfile user={self.user_id}, {self.portion_grams}g @ {self.feed_times} on {self.days}>"

def check_and_feed(profiles):
    for profile in profiles:
        if profile.is_active_now():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FEEDING: User {profile.user_id}'s cat should be fed {profile.portion_grams}g now.")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SKIP: No feeding needed now for {profile.user_id}.")

if __name__ == "__main__":
    profiles = [
        FeedingProfile(
            user_id="sarah123",
            portion_grams=50,
            feed_times=["08:00", "18:00"],
            days=["Monday", "Wednesday", "Friday"],
            start_date="2025-03-01",
            end_date="2025-04-01"
        ),
        FeedingProfile(
            user_id="alex456",
            portion_grams=70,
            feed_times=["12:00", "16:00", "20:00"],
            days="daily",
            start_date="2025-03-01",
            end_date="2025-12-31"
        )
    ]
    while True:
        check_and_feed(profiles)
        print("Waiting 60 seconds before checking again...\n")
        time.sleep(60)
