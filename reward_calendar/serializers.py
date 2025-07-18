from rest_framework import serializers
from .models import RewardCalendar

class RewardCalendarSerializer(serializers.ModelSerializer):
    sticker_label = serializers.SerializerMethodField()

    class Meta:
        model = RewardCalendar
        fields = [
            'id', 'child', 'date', 'sticker_type', 'sticker_label',
            'message', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'child', 'sticker_label', 'created_at', 'updated_at']

    def validate(self, attrs):
        # 수정일 때
        if self.instance:
            if 'date' not in attrs:
                raise serializers.ValidationError({'date': '수정 시 date는 필수입니다.'})
        else:
            # 생성일 때
            if 'sticker_type' not in attrs:
                raise serializers.ValidationError({'sticker_type': '생성 시 sticker_type은 필수입니다.'})
        return attrs

    def get_sticker_label(self, obj):
        return obj.get_sticker_type_display()