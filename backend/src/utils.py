"""
Utility functions for the AdultingOS backend.
"""

def format_response(data, status="success", message=""):
    """
    Format the API response in a consistent structure.
    
    Args:
        data: The actual data payload to return
        status: Status of the response ('success' or 'error')
        message: Optional message to include
        
    Returns:
        Dictionary with formatted response
    """
    return {
        "status": status,
        "message": message,
        "data": data
    }


def validate_input(data, required_fields):
    """
    Validate that the input data contains all required fields.
    
    Args:
        data: The input data to validate
        required_fields: List of field names that must be present
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    if not data:
        return False, required_fields
        
    missing = [field for field in required_fields if field not in data]
    
    return len(missing) == 0, missing
