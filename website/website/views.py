from django.views.generic import TemplateView
from rest_framework import generics, mixins
from base import serializers
import pusher
from django.conf import settings
from django.forms.models import model_to_dict
from rest_framework.response import Response


pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster='eu',
    ssl=False
)


class HomeView(TemplateView):
    template_name = "home.html"


class PostDataView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = serializers.WaveDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model = serializer.save()
        model_dict = model_to_dict(model)

        pusher_client.trigger(
            'brain_channel', 'data_received',
            {'data': model_dict}
        )

        return Response(serializer.data, status=201)


def get_file(request):
    from django.conf import settings
    from django.core.servers.basehttp import FileWrapper
    from django.shortcuts import HttpResponse

    import os

    filename = os.path.join(settings.BASE_DIR, "the_mp3.mp3")
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='audio/mp3')
    response['Content-Length'] = os.path.getsize(filename)
    return response
