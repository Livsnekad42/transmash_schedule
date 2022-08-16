from core.permissions.manager import ManagerPermission


class ManagerCompanyPermission(ManagerPermission):
    module_name = "module_admin"


class ManagerRoleCompanyPermission(ManagerPermission):
    module_name = "module_manager"
