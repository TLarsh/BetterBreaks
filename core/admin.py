# from core.admins import (
#     action_data_admins,
#     badge_admins,
#     contact_admins,
#     date_admins,
#     holiday_admins,
#     leave_balance_admins,
#     onboarding_admins,
#     preference_admins,
#     setting_admins,
#     user_admins,
#     recommendation_admins,
# )




import os
import importlib

from django.conf import settings

admin_folder = os.path.join(os.path.dirname(__file__), 'admins')
for filename in os.listdir(admin_folder):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = f'core.admins.{filename[:-3]}'
        importlib.import_module(module_name)
