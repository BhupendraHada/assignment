from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.Serializer):
    """
    Serializer for User internal API
    """
    inputData = serializers.JSONField()

    def validate(self, value):
        """
        :param value:
        :return:
        """
        if value.get('inputData'):
            details_json = value.get('inputData')
            user_obj = User.objects.filter(id=int(details_json.get("user_id"))).last()
            if user_obj:
                if details_json:
                    transaction_key_list = ["user_id", "username", "first_name", "last_name"]
                    if all([key in transaction_key_list for key in details_json]):
                        return value
                    else:
                        raise serializers.ValidationError("All user data keys are not exist.")
                else:
                    raise serializers.ValidationError("User details are not exist.")
            else:
                raise serializers.ValidationError(str({"id": "User id does not exist."}))