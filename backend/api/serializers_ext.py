from rest_framework import serializers
from .models import Attendee, Company, Registration, Certificate

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'contact_email', 'contact_phone']

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'company', 'company_name', 'position', 'participant_type', 'registered_at', 'qr_code'
        ]

class RegistrationSerializer(serializers.ModelSerializer):
    attendee = AttendeeSerializer(read_only=True)
    attendee_id = serializers.PrimaryKeyRelatedField(queryset=Attendee.objects.all(), source='attendee', write_only=True)
    class Meta:
        model = Registration
        fields = ['id', 'attendee', 'attendee_id', 'event_name', 'status', 'registered_at', 'attended_at', 'certified_at']

class CertificateSerializer(serializers.ModelSerializer):
    registration = RegistrationSerializer(read_only=True)
    registration_id = serializers.PrimaryKeyRelatedField(queryset=Registration.objects.all(), source='registration', write_only=True)
    class Meta:
        model = Certificate
        fields = ['id', 'registration', 'registration_id', 'pdf', 'sent', 'sent_at', 'created_at']
