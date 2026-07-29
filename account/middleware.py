import json
from django.utils.deprecation import MiddlewareMixin

class CustomerAccountStorageMiddleware(MiddlewareMixin):
    """
    Middleware to ensure that the currently authenticated Customer
    is saved into the 'garud_customer_accounts' cookie.
    """
    def process_response(self, request, response):
        # We only care if the user is authenticated and is a Customer
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if user has Customer role
            is_customer = False
            if hasattr(request.user, 'roles') and request.user.roles:
                if request.user.roles.name == 'Customer':
                    is_customer = True
            
            if is_customer:
                session_key = request.session.session_key
                if session_key:
                    # Read existing accounts from cookie
                    cookie_name = 'garud_customer_accounts'
                    saved_accounts_str = request.COOKIES.get(cookie_name, '{}')
                    
                    try:
                        saved_accounts = json.loads(saved_accounts_str)
                    except json.JSONDecodeError:
                        saved_accounts = {}
                        
                    user_id_str = str(request.user.id)
                    
                    # Create/Update account entry
                    account_data = {
                        'id': request.user.id,
                        'mobile': str(request.user.mobile),
                        'name': request.user.fullname or 'Customer',
                        'email': request.user.email or '',
                        'session_key': session_key,
                        # Add timestamp to know when it was last active
                        'last_active': request.user.last_login.isoformat() if request.user.last_login else ''
                    }
                    
                    # Only update cookie if something changed to avoid unnecessary Set-Cookie headers
                    current_saved = saved_accounts.get(user_id_str)
                    if not current_saved or current_saved.get('session_key') != session_key or current_saved.get('name') != account_data['name']:
                        saved_accounts[user_id_str] = account_data
                        
                        # Set cookie for 1 year
                        response.set_cookie(
                            cookie_name, 
                            json.dumps(saved_accounts), 
                            max_age=31536000, 
                            httponly=True, 
                            samesite='Lax'
                        )
                        
        return response
