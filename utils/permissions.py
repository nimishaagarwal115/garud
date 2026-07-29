from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Admin']).exists()

    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name__in=['Owner', 'Admin']).exists()
    
class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        # Allow unauthenticated access to the `register` action in UserVIewSet
        if view.action == 'register':
            return True
        
        return request.user.is_authenticated and (request.user.is_staff or request.current_business is not None)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return request.current_business.has_user_role(obj)

class IsAuthenticatedWithCurrentBusiness(BasePermission):
    """
    Permission class to check if the user is authenticated and has a current business.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request, 'current_business') and request.current_business is not None


class HasValidBusiness(BasePermission):
    message = "You must have a valid business to perform this operation."

    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')
        if request.method in methods:
            business = request.current_business        
            # Check if the user has an active subscription        
            return business is not None
        else:
            return True

class HasActiveSubscription(BasePermission):
    message = "You must have an active subscription to perform this action"

    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')
        if request.method in methods: 
            user = request.user
            # Check if the user has an active subscription
            return user.subscription_status(request) != "unsubscribed"
        else:
            return True


class IsBusinessAdmin(BasePermission):
    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')        
        if request.method in methods:            
            if not request.user.role(request) in ["Admin", "Owner"]:
                raise ValueError("User doesn't have required permissions")             
            return True
        else:
            return True
    

class IsBusinessManager(BasePermission):
    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')
        if request.method in methods:
            if not request.user.role(request) == "Manager":
                raise ValueError("User doesn't have required permissions")             
            return True
        else:
            return True
        

class IsFieldOfficer(BasePermission):
    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')
        if request.method in methods:
            if not request.user.role(request) == "Officer":
                raise ValueError("User doesn't have required permissions")             
            return True
        else:
            return True
        

class IsHigherAuthorities(BasePermission):
    def has_permission(self, request, view):
        methods = getattr(view, 'SAFE_METHODS')        
        if request.method in methods:
            if request.user.role(request) in ["Officer", "Independent", "Client"]:
                raise ValueError("User doesn't have required permissions")             
            return True
        else:
            return True
        
    