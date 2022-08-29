from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from company.models import Company, Department
from geo_city.models import Address


class Skill(models.Model):
    name = models.CharField(null=True, blank=True, max_length=20, verbose_name="Тип оборудования")

    class Meta:
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Типы оборудования'


class SkillLevel(models.Model):
    LEVEL = (
        ("Отлично", "Отлично"),
        ("Хорошо", "Хорошо"),
        ("Удовлетворительно", "Удовлетворительно"),
        ("Неудовлетворительно", "Неудовлетворительно")
    )

    grade = models.CharField(choices=LEVEL, null=True, blank=True, max_length=20, verbose_name='Уровень навыков')

    class Meta:
        verbose_name = 'Профессиональный навык'
        verbose_name_plural = 'Профессиональные навыки'


class EmployeeTechSkill(models.Model):
    skill = models.ForeignKey(Skill, related_name='employee_tech_skill', on_delete=models.SET_NULL, null=True)
    skill_level = models.ForeignKey(SkillLevel, related_name='employee_tech_skill_level', on_delete=models.SET_NULL,
                                    null=True)

    class Meta:
        verbose_name = 'Профессиональный навык'
        verbose_name_plural = 'Профессиональные навыки'


class BranchRequirementSKill(models.Model):
    skill = models.ForeignKey(Skill, related_name='employee_req_skill', on_delete=models.SET_NULL, null=True)
    skill_level = models.ForeignKey(SkillLevel, related_name='employee_req_skill_level', on_delete=models.SET_NULL,
                                    null=True)

    class Meta:
        verbose_name = 'Профессиональный навык'
        verbose_name_plural = 'Профессиональные навыки'


class Branch(models.Model):
    name = models.CharField(_('branch name'), max_length=255, unique=True)
    company = models.ForeignKey(Company, related_name='branches', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    requirements = models.ForeignKey(BranchRequirementSKill, related_name='requirement_branch', null=True, on_delete=models.SET_NULL, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('branch')
        verbose_name_plural = _('branches')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address.to_dict(),
        }


class Personal(models.Model):
    PCYCHO = (
        ("1", "Высокий уровень"),
        ("2", "Средний уровень"),
        ("3", "Низкий уровень"),

    )
    responsibility = models.CharField(choices=PCYCHO, null=True, blank=True, max_length=20,
                                      verbose_name="Ответственность")
    sociability = models.CharField(choices=PCYCHO, null=True, blank=True, max_length=20,
                                   verbose_name="Коммуникабельность")
    stress = models.CharField(choices=PCYCHO, null=True, blank=True, max_length=20, verbose_name="Стрессоустойчивость")
    conflict = models.CharField(choices=PCYCHO, null=True, blank=True, max_length=20, verbose_name="Конфликтность")

    class Meta:
        verbose_name = 'Личные качества'
        verbose_name_plural = 'Личные качества'


class Employee(models.Model):
    LEVEL_CATEGORY = (
        ("1", "1-я"),
        ("2", "2-я"),
        ("3", "3-я")
    )
    SENIORITY_LIST = (
        ("Инженер", "Инженер"),
        ("Стажер", "Стажер"),
    )
    name = models.CharField(max_length=255, verbose_name='Имя')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name='Фото', null=True)
    seniority = models.CharField(choices=SENIORITY_LIST, max_length=20, null=True, verbose_name='Должность')
    cat = models.CharField(choices=LEVEL_CATEGORY, max_length=10, null=True, verbose_name='Категория')
    explored_branches = models.ForeignKey(Branch, on_delete=models.PROTECT, null=True,
                                          verbose_name='Знакомые объекты')  # Выбираются все шахты, на которых
    # сотрудник работал 2 недели и более
    favorite_branch = models.ForeignKey(Branch, related_name='favoritebranches', on_delete=models.PROTECT, null=True,
                                        verbose_name='Предпочитаемый объект')
    department = models.ForeignKey(Department, related_name='department_employee', on_delete=models.CASCADE,
                                   verbose_name='Участок', null=True)
    employee_tech_skill = models.ManyToManyField(EmployeeTechSkill, related_name='tech_skill_employee', verbose_name='Уровень навыков', null=True)
    personal_qualities = models.ForeignKey(Personal, on_delete=models.PROTECT, null=True,
                                           verbose_name='Личные качества')
    medical = models.TextField(blank=False, verbose_name='Мединформация', null=True)
    special = models.TextField(blank=False, verbose_name='Особые отметки', null=True)

    class Meta:
        verbose_name = 'Сотрудники'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_id': self.pk})
