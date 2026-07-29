from django.db.models.signals import post_save 
from django.dispatch import receiver 
from account.models import UserProfileModel
from django.contrib.auth import get_user_model
User = get_user_model()

# This decorator connects the create_user_profile function to the post_save signal
# It specifically listens for save events on the User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler that automatically creates a UserProfile when a new CustomUser is created.
    
    Parameters:
        sender: The model class that sent the signal (User)
        instance: The actual instance of User that was saved
        created: Boolean flag indicating if this is a new instance (True) or an update (False)
        **kwargs: Additional keyword arguments passed by the signal
    """
    if created:  # Only execute for newly created users, not updates to existing users
        UserProfileModel.objects.create(user=instance)  # Create a profile linked to the new user