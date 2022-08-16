from rest_framework import serializers

from administration.models import CompanyPlan, CompanyBilling, UserPlan, UserBilling


class CompanyBillingSerializer(serializers.ModelSerializer):
    number_managers = serializers.IntegerField(default=0, required=False, allow_null=True)
    number_established_branches = serializers.IntegerField(default=0, required=False, allow_null=True)
    number_megabytes_disk = serializers.IntegerField(default=0, required=False, allow_null=True)
    number_goods_services = serializers.IntegerField(default=0, required=False, allow_null=True)
    notification = serializers.BooleanField(default=False, required=False, allow_null=True)
    landing = serializers.BooleanField(default=False, required=False, allow_null=True)
    report = serializers.BooleanField(default=False, required=False, allow_null=True)
    number_tasks = serializers.IntegerField(default=0, required=False, allow_null=True)
    documents_template = serializers.BooleanField(default=False, required=False, allow_null=True)
    analytics = serializers.BooleanField(default=False, required=False, allow_null=True)
    dashboard = serializers.BooleanField(default=False, required=False, allow_null=True)

    class Meta:
        model = CompanyBilling
        fields = (
            'number_managers',
            'number_established_branches',
            'number_megabytes_disk',
            'number_goods_services',
            'notification',
            'landing',
            'report',
            'number_tasks',
            'documents_template',
            'analytics',
            'dashboard',
        )


class UserBillingSerializer(serializers.ModelSerializer):
    number_family_tree_nodes = serializers.IntegerField(default=0)
    number_megabytes_disk = serializers.IntegerField(default=0)
    number_memory_page = serializers.IntegerField(default=0)

    class Meta:
        model = UserBilling
        fields = (
            'number_family_tree_nodes',
            'number_megabytes_disk',
            'number_memory_page',
        )


class CompanyPlanSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_archive = serializers.BooleanField(default=False, required=False, allow_null=True)
    tariff = CompanyBillingSerializer()

    class Meta:
        model = CompanyPlan
        fields = (
            'id',
            'title',
            'price',
            'is_archive',
            'tariff',
        )

    def create(self, validated_data):
        tariff_data = validated_data.pop("tariff")

        tariff_instance = CompanyBilling.objects.create(**tariff_data)
        validated_data["tariff"] = tariff_instance

        return CompanyPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        tariff_data = validated_data.pop("tariff")

        for (key, value) in tariff_data.items():
            setattr(instance.tariff, key, value)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.tariff.save()
        instance.save()

        return instance


class UserPlanSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_archive = serializers.BooleanField(default=False, required=False, allow_null=True)
    tariff = UserBillingSerializer()

    class Meta:
        model = UserPlan
        fields = (
            'id',
            'title',
            'price',
            'is_archive',
            'tariff',
        )

    def create(self, validated_data):
        tariff_data = validated_data.pop("tariff")

        tariff_instance = UserBilling.objects.create(**tariff_data)
        validated_data["tariff"] = tariff_instance

        return UserPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        tariff_data = validated_data.pop("tariff")

        for (key, value) in tariff_data.items():
            setattr(instance.tariff, key, value)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.tariff.save()
        instance.save()

        return instance
