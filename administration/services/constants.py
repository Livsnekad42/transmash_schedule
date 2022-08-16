from enum import Enum

from administration.models import CompanyPlan, UserPlan, PromoCodes, Partner, GeoModule, UserModule, CompanyModule, \
    AdminModule
from company.models import Company, Manager, Role
from geo_city.models import Country, Region, City, Street, Place, Address
from profiles.models import Profile


class PermissionAdmin(Enum):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"
    VIEW = "view"


GEO_MODULE = (
    Country,
    Region,
    City,
    Street,
    Place,
    Address,
)

USER_MODULE = (
    Profile
)

COMPANY_MODULE = (
    Company,
    Manager,
    Role
)

ADMIN_MODULE = (
    CompanyPlan,
    UserPlan,
    PromoCodes,
    Partner,
)

ADMIN_MODULES = [
    {
        "name": "geo",
        "title": "Гео модуль",
        "models": GEO_MODULE,
        "model": GeoModule,
    },
    {
        "name": "users",
        "title": "Пользователи",
        "models": USER_MODULE,
        "model": UserModule,
    },
    {
        "name": "company",
        "title": "Компании",
        "models": COMPANY_MODULE,
        "model": CompanyModule,
    },
    {
        "name": "admin",
        "title": "Админпанель",
        "models": ADMIN_MODULE,
        "model": AdminModule,
    },
]



