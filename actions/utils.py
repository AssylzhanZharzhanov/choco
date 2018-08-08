from django.utils import timezone
import  datetime
from .models import Action

def create_action(user, verb, ids):
    # now = timezone.now()
    # last_minute = now - datetime.timedelta(seconds=60)
    # similar_actions = Action.objects.filter(user_id=user.id,
    #                                    verb= verb,
    #                                    timestamp__gte=last_minute)
    # if not similar_actions:
        action = Action(user=user, verb=verb, ids=ids)
        action.save()
        # return  True
    # return False