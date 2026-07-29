from rest_framework.response import Response
import ast
import traceback

def success_response(data=None, message="Success", status_code=200):
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    return Response(response, status=status_code)

def error_response(errors=None, message="Error", status_code=400):
    response = {
        "status": "error",
        "message": message,
        "errors": parse_errors(errors)
    }
    return Response(response, status=status_code)

def parse_errors(errors):    
    if isinstance(errors, str):
        try:
            print(f"this is string")
            # Handle ErrorDetail string format
            if "ErrorDetail" in errors:
                # Extract the inner dictionary or message from the ErrorDetail string
                start = errors.find("{")
                end = errors.rfind("}") + 1
                if start != -1 and end != -1:
                    errors = errors[start:end]
                    
            # Attempt to parse the string as a dictionary or list
            parsed_errors = ast.literal_eval(errors)            
            if isinstance(parsed_errors, dict):
                # If the dictionary has a single key '__all__', return its value as a list
                if '__all__' in parsed_errors:
                    return parsed_errors['__all__']
                return parsed_errors
            elif isinstance(parsed_errors, list):
                return [str(error) for error in parsed_errors]
        except (ValueError, SyntaxError):
            print(traceback.format_exc())
            # If parsing fails, return the original string wrapped in a list
            return [errors]
    elif isinstance(errors, dict):
        # If the dictionary has a single key '__all__', return its value as a list
        if '__all__' in errors:
            return errors['__all__']
        return errors
    elif isinstance(errors, list):
        # Convert ErrorDetail objects to string
        return [str(error) if isinstance(error, str) else error.get('string', str(error)) for error in errors]
    return [errors]