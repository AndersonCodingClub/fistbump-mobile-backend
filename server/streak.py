from datetime import date
from database import Database


class Streak:
    @staticmethod
    def handle_streak(user_id: int, increment: bool=False) -> int:
        d = Database()
        rows = d.get_images(user_id)
        if len(rows) == 0:
            return 0
        
        most_recent_image_row = rows[-1]
        last_picture_date = most_recent_image_row[-1].date()
        current_date = date.today()
        day_difference = (current_date - last_picture_date).days
        
        if day_difference >= 2:
            if increment:
                return d.set_streak(user_id, 1)
            else:
                return d.set_streak(user_id, 0)
        else:
            if increment and day_difference == 1:
                return d.increment_streak(user_id)
            elif increment and day_difference == 0 and len(rows) == 1:
                return d.increment_streak(user_id)
            else:
                return d.get_streak(user_id)