# from django.dispatch import receiver
# from .signals import operation_signal
# from .services import CommunicationService
# import json
# import requests

# action_map = {
#     'Create business': {
#         'screen': 'SelectBusiness',
#         'message': 'A new business has been added to your account.',
#         'receivers': lambda business: business.ownerAndAdmin,  # Group of users
#         'notification_types': ['push', 'email'],  # Send push and email notifications
#     },
#     'Update business': {
#         'screen': 'SelectBusiness',
#         'message': 'Your business has been updated.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete business': {
#         'screen': 'SelectBusiness',
#         'message': 'Your business has been deleted.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Create client': {
#         'screen': 'ClientList',
#         'message': 'A new client has been added to your business.',
#         'receivers': lambda business: business.clientManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Create site': {
#         'screen': 'SiteList',
#         'message': 'A new site has been added to your business.',
#         'receivers': lambda business: business.siteManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Update site': {
#         'screen': 'SiteList',
#         'message': 'Your site has been updated.',
#         'receivers': lambda business: business.siteManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete site': {
#         'screen': 'SiteList',
#         'message': 'Your site has been deleted.',
#         'receivers': lambda business: business.siteManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Create checkpoint': {
#         'screen': 'CheckPointList',
#         'message': 'A new checkpoint has been added to your site.',
#         'receivers': lambda business: business.securityOfficers,
#         'notification_types': ['push', 'email'],
#     },
#     'Update checkpoint': {
#         'screen': 'CheckPointList',
#         'message': 'Your checkpoint has been updated.',
#         'receivers': lambda business: business.securityOfficers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete checkpoint': {
#         'screen': 'CheckPointList',
#         'message': 'Your checkpoint has been deleted.',
#         'receivers': lambda business: business.securityOfficers,
#         'notification_types': ['push', 'email'],
#     },
#     'Create route': {
#         'screen': 'RouteList',
#         'message': 'A new route has been added to your site.',
#         'receivers': lambda business: business.routeManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Update route': {
#         'screen': 'RouteList',
#         'message': 'Your route has been updated.',
#         'receivers': lambda business: business.routeManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete route': {
#         'screen': 'RouteList',
#         'message': 'Your route has been deleted.',
#         'receivers': lambda business: business.routeManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Create officer on route': {
#         'screen': 'FieldOfficerList',
#         'message': 'A new duty officer has been added to your route.',
#         'receivers': lambda business: business.routeManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete officer on route': {
#         'screen': 'FieldOfficerList',
#         'message': 'A duty officer has been removed from your route.',
#         'receivers': lambda business: business.routeManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Create duty': {
#         'screen': 'Report',
#         'message': 'Your officer started duty.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'sms'],  # Send push and SMS notifications
#     },
#     'Update duty': {
#         'screen': 'Report',
#         'message': 'Your officer completed duty.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'sms'],
#     },
#     'Create checkpoint report': {
#         'screen': 'CheckPointReport',
#         'message': 'Your officer added a checkpoint report.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Update checkpoint report': {
#         'screen': 'CheckPointReport',
#         'message': 'Your officer updated a checkpoint report.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete checkpoint report': {
#         'screen': 'CheckPointReport',
#         'message': 'Your officer deleted a checkpoint report.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Create employee': {
#         'screen': 'FieldOfficerList',
#         'message': 'Your employee has been added successfully.',
#         'receivers': lambda business: business.hrManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Update employee': {
#         'screen': 'FieldOfficerList',
#         'message': 'Your employee has been updated successfully.',
#         'receivers': lambda business: business.hrManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete employee': {
#         'screen': 'FieldOfficerList',
#         'message': 'Your employee has been deleted successfully.',
#         'receivers': lambda business: business.hrManagers,
#         'notification_types': ['push', 'email'],
#     },
#     'Delete role': {
#         'screen': 'FieldOfficerList',
#         'message': 'A role has been deleted successfully.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
#     'Update role': {
#         'screen': 'FieldOfficerList',
#         'message': 'A role has been updated successfully.',
#         'receivers': lambda business: business.ownerAndAdmin,
#         'notification_types': ['push', 'email'],
#     },
# }

# @receiver(operation_signal)
# def handle_crud_operation(user, current_business, action, instance, id, **kwargs):
#     # Fetch action details from action_map
#     action_details = action_map.get(action, None)
#     if not action_details:
#         # If the action is not defined in action_map, skip processing
#         return

#     # Extract details from action_map
#     message = action_details['message']
#     screen = action_details['screen']
#     get_receivers = action_details['receivers']
#     notification_types = action_details['notification_types']

#     # Dynamically fetch receivers
#     receivers = get_receivers(current_business)

#     # Extract contact details from the receivers
#     phone_numbers = [receiver.phone_number for receiver in receivers if receiver.phone_number]
#     whatsapp_numbers = [receiver.phone_number for receiver in receivers if receiver.phone_number]
#     push_tokens = [receiver.expo_push_token for receiver in receivers if receiver.expo_push_token]
#     email_addresses = [receiver.email for receiver in receivers if receiver.email]

#     # Add screen identifier and link to the push notification payload
#     push_payload = {
#         "message": message,
#         "screen": screen,
#         "data": {
#             "icon": "https://api2.securityforce.in/static/dashboard/img/favicon/favicon.png",
#             "link": f"securityforce://{screen}/{id}" if id else f"securityforce://{screen}",
#         },
#     }

#     # Send notifications based on the specified types
#     if 'sms' in notification_types and phone_numbers:
#         CommunicationService.send_sms(message, phone_numbers)

#     if 'whatsapp' in notification_types and whatsapp_numbers:
#         CommunicationService.send_whatsapp_message(message, whatsapp_numbers)

#     if 'push' in notification_types and push_tokens:
#         CommunicationService.send_push_notification(push_payload, push_tokens)

#     if 'email' in notification_types and email_addresses:
#         CommunicationService.send_email("Notification", message, email_addresses)
