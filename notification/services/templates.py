from notification.services.alerts import NotifyTemplate

ALERTS = {
    "created_manager": NotifyTemplate("created_manager.tpl"),
    "add_to_role": NotifyTemplate("add_to_role.tpl"),
    "new_task": NotifyTemplate("new_task.tpl"),
}
