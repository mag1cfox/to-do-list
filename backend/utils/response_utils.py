from typing import Dict, Any, Optional
from flask import jsonify


def success_response(data: Optional[Dict[str, Any]] = None, message: str = "Success", status_code: int = 200):
    """成功响应格式"""
    response = {
        'success': True,
        'message': message,
        'data': data or {}
    }
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
    """错误响应格式"""
    response = {
        'success': False,
        'message': message,
        'error': {
            'code': status_code,
            'details': details or {}
        }
    }
    return jsonify(response), status_code


def validation_error_response(errors: Dict[str, Any]):
    """验证错误响应"""
    return error_response(
        message="Validation failed",
        status_code=422,
        details={'validation_errors': errors}
    )