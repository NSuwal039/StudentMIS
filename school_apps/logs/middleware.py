from django.db.models import signals
from functools import partial
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from .models import UserLog
from django.dispatch import receiver
from django.db.models.signals import post_save
from functools import partial as curry
from rest_framework.authtoken.models import Token
import geoip2.webservice
# from notifications.models import Notification
from user_agents import parse


class UserLoggingMiddleware(object):
    ip_address = None
    def __init__(self, get_response):
        self.get_response = get_response
    
    
    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            print("in middleware")
            try:
                token = request.META.get('HTTP_AUTHORIZATION')
                token_key = token.split(" ")[1]
                user = Token.objects.get(key=token_key).user
            except:
                user=None

            session = request.session.session_key
            self.ip_address = request.META.get('REMOTE_ADDR', None)
            user_agent = request.META['HTTP_USER_AGENT']
            try:
                client = geoip2.webservice.Client(670479, 'gLAn9GhLLVQ3ph6Q', host='geolite.info')
                response = client.city(self.ip_address)
                self.location = str(response.country.name) + " " + str(response.city.name)
            except:
                self.location=None
            
            ua_string = user_agent
            user_agent=parse(ua_string)
            ua_str=str(user_agent)
            self.device = ua_str.split("/")[0].replace(" ","")+ " " +ua_str.split("/")[1].replace(" ","")
            self.user_agent = user_agent.browser.family + " " + user_agent.browser.version_string

            update_post_save_info = curry(
                self._update_post_save_info,
                user,
                session,
            )
            update_post_delete_info = curry(
                self._update_post_delete_info,
                user,
                session,
            )
            signals.post_save.connect(
                update_post_save_info,
                dispatch_uid=(self.__class__, request,),
                weak=False
            )
            signals.post_delete.connect(
                update_post_delete_info,
                dispatch_uid=(self.__class__, request,),
                weak=False
            )

    def _save_to_log(self, instance, action, user):

        pass
        # print(user)
        content_type = ContentType.objects.get_for_model(instance)
        if content_type.app_label != 'user_log' and user:
            object_id = instance.pk 
            # print(object_id)
            try:
                object_instance_str=serializers.serialize('json', [instance])
            except:
                object_instance_str="[]"

            userlog = UserLog( 
                object_id=object_id,
                app_name=content_type.app_label,
                model_name=content_type.model,
                action=action,
                object_instance=object_instance_str,
                user=user,
                ip=self.ip_address,
                user_agent = self.user_agent,
                location = self.location,
                device=self.device
            )
            if UserLog.objects.all().count():
                last_log = UserLog.objects.latest('id')
                if not last_log.__eq__(userlog):
                    userlog.save()
            else:
                userlog.save()
                    
    def _update_post_save_info(
            self,
            user,
            session,
            sender,
            instance,
            **kwargs
    ):
        if sender in [UserLog,LogEntry,Session]:
            return None
        if kwargs['created']:
            self._save_to_log(instance, UserLog.ACTION_TYPE_CREATE, user)
        else:
            self._save_to_log(instance, UserLog.ACTION_TYPE_UPDATE, user)

    def _update_post_delete_info(
            self,
            user,
            session,
            sender,
            instance,
            **kwargs
    ):
        if sender in [UserLog,LogEntry, Session]:
            return None
        self._save_to_log(instance, UserLog.ACTION_TYPE_DELETE, user)