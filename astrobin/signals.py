# Django
from django.core.urlresolvers import reverse as reverse_url
from django.db.models.signals import m2m_changed
from django.db.models.signals import post_save

# Other AstroBin apps
from nested_comments.models import NestedComment
from rawdata.models import RawImage, PublicDataPool

# This app
from .notifications import push_notification
from .models import Image, Gear, UserProfile
from .gear import get_correct_gear


def nested_comment_post_save(sender, instance, created, **kwargs):
    if created:
        model_class = instance.content_type.model_class()
        obj = instance.content_type.get_object_for_this_type(id = instance.object_id)
        url = instance.get_absolute_url()

        if model_class == Image:
            if instance.author != obj.user:
                push_notification(
                    [obj.user], 'new_comment',
                    {
                        'url': url,
                        'user': instance.author,
                    }
                )
 
            if instance.parent and instance.parent.author != instance.author:
                push_notification(
                    [instance.parent.author], 'new_comment_reply',
                    {
                        'url': url,
                        'user': instance.author,
                    }
                )
     
        elif model_class == Gear:
            if not instance.parent:
                gear, gear_type = get_correct_gear(obj.id)
                user_attr_lookup = {
                    'Telescope': 'telescopes',
                    'Camera': 'cameras',
                    'Mount': 'mounts',
                    'FocalReducer': 'focal_reducers',
                    'Software': 'software',
                    'Filter': 'filters',
                    'Accessory': 'accessories',
                }

                recipients = [x.user for x in UserProfile.objects.filter(
                    **{user_attr_lookup[gear_type]: gear})]
                notification = 'new_gear_discussion'
            else:
                notification = 'new_comment_reply'
                recipients = [instance.parent.author]

            push_notification(
                recipients, notification,
                {
                    'url': url,
                    'user': instance.author,
                }
            )


def rawdata_publicdatapool_data_added(sender, instance, action, reverse, model, pk_set, **kwargs):
    if not instance.creator:
        return

    if action == 'post_add' and len(pk_set) > 0:
        contributors = [i.user for i in instance.images.all()]
        users = [instance.creator] + contributors
        submitter = RawImage.objects.get(pk = list(pk_set)[0]).user
        push_notification(
            users,
            'rawdata_posted_to_pool',
            {
                'user_name': submitter.username,
                'user_url': reverse_url('user_page', kwargs = {'username': submitter.username}),
                'pool_name': instance.name,
                'pool_url': reverse_url('rawdata.publicdatapool_detail', kwargs = {'pk': instance.pk}),
            },
        )


post_save.connect(nested_comment_post_save, sender = NestedComment)
m2m_changed.connect(rawdata_publicdatapool_data_added, sender = PublicDataPool.images.through)
