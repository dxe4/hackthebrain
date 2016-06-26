from rest_framework import serializers
from base.models import WaveData


class WaveDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaveData
