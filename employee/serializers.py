from abc import ABC
from django.forms import models
from rest_framework import serializers

from company.models import Company
from geo_city.serializers import AddressSerializer
from .models import Skill, SkillLevel, Branch, Personal, Employee, BranchRequirementSKill, EmployeeTechSkill
from rest_framework.renderers import JSONRenderer


# class EmployeeModel:
#  def __init__(self, name, seniority):
#    self.name = name
#  self.seniority = seniority
#


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model: Personal
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class SkillLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillLevel
        fields = "__all__"


class BranchRequirementSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(required=False)
    skill_level = SkillLevelSerializer(required=False)

    class Meta:
        model: BranchRequirementSKill
        fields = "__all__"


class BranchSerializer(serializers.ModelSerializer):
    requirements = BranchRequirementSkillSerializer(required=False, allow_null=True)
    id = serializers.IntegerField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Branch
        fields = (
            'id',
            'name',
            'address',
            'description',
            'phone',
            'email',
            'company',
            'requirements'
        )

    def create(self, validated_data):
        address = validated_data.pop("address", None)

        if address:
            address_instance = AddressSerializer.update_or_create(address)
        else:
            address_instance = None

        return Branch.objects.create(**validated_data, address=address_instance)

    def update(self, instance, validated_data):
        address = validated_data.pop("address", None)

        if address:
            address_instance = AddressSerializer.update_or_create(address)
        else:
            address_instance = None

        instance.address = address_instance
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class EmployeeTechSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(required=False)
    skill_level = SkillLevelSerializer(required=False)

    class Meta:
        model: EmployeeTechSkill
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=40, allow_null=True, allow_blank=True, required=False)
    employee_tech_skill = EmployeeTechSkillSerializer(many=True, required=False)
    photo = serializers.ImageField(required=False)
    explored_branches = BranchSerializer(required=False, many=True)

    class Meta:
        model = Employee
        fields = "__all__"

    def create(self, validated_data):
        skills_level = validated_data.pop("skills_level", None)
        skills_instances = []
        if skills_level is not None:
            # for skill in skills_level:
            #     skills_id = skill.get("id", None)
            #     if skills_id:
            #         try:
            #             skills_instance = Skills.objects.get(id=skills_id)
            #             skills_instance.name = skill.name
            #             skills_instance.grade = skill.grade
            #             skills_instance.save()
            #             skills_level.pop(skill)
            #         except Skills.DoesNotExist:
            #             raise ValueError("???????????? id ???? ??????????????")
            skills_level_serializer = EmployeeTechSkillSerializer(data=skills_level, many=True)
            skills_level_serializer.is_valid(raise_exception=True)
            skills_instances = skills_level_serializer.save()
        instance = Employee.objects.create(**validated_data)
        for skill in skills_instances:
            instance.skills_level.add(skill)
        instance.save()

        return instance
    # name = serializers.CharField(max_length=255)
    # photo = serializers.ImageField(read_only=True)
    # photo_upload = serializers.CharField(write_only=True, required=False)

    # cat = serializers.CharField(read_only=True)
    # explored_branches = BranchesSerializer(read_only=True)  # ???????????????????? ?????? ??????????, ???? ?????????????? ?????????????????? ?????????????? 2 ???????????? ?? ??????????
    # favorite_branch = BranchesSerializer(read_only=True)  # ???????????????????? ???????? ??????????
    # skills_level = SkillsSerializer(required=False, allow_null=True)
    # personal_qualities = PersonalSerializer(read_only=True)
    # medical = serializers.CharField(read_only=True)
    # special = serializers.CharField(read_only=True)

    # class Meta:
    #    model: Employee
    #    fields = "__all__"

    # def create(self, validated_data):
    #   return Employee.objects.create(**validated_data)
    #   #skills = validated_data.pop("skills", None)
    #   #logo_upload = validated_data.pop("logo_upload", None)
    #  #address = validated_data.pop("address_id", None)
    #  #organizational_legal_form = validated_data.pop("organizational_legal_form", None)
    # bank_details = validated_data.pop("bank_details", None)

    # def update(self, instance, validated_data):
    #   instance.name = validated_data.get('name', instance.name)
    #  instance.seniority = validated_data.get('seniority', instance.seniority)
    # instance.cat = validated_data.get('cat', instance.cat)
    # instance.explored_branches = validated_data.get('explored_branches', instance.explored_branches)
    # instance.favorite_branch = validated_data.get('favorite_branch', instance.favorite_branch)
    # #instance.skills_level = validated_data.get('skills_level', instance.skills_level)
    # instance.personal_qualities = validated_data.get('personal_qualities', instance.personal_qualities)
    # instance.medical = validated_data.get('medical', instance.medical)
    # instance.special = validated_data.get('special', instance.special)
    # instance.save()
    # return instance

    # def delete(self, instance):

    # if logo_upload is not None:
    #  try:
    #   _logo_file = get_img_from_data_url(logo_upload)[0]
    # except Exception:
    #  raise serializers.ValidationError(_('Not valid media "image".'))

    # validated_data["logo"] = _logo_file

# def validate(self, attrs):
# return attrs


# def encode():
#   model = EmployeeModel('Rodichkin Andrey', 'Seniority: Ingineer')
#  model_sr = EmployeeSerializer(model)
# json = JSONRender().render(model_sr.data)
# print(json)
