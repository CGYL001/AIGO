"""
认证和用户管理相关的API路由
"""

import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from src.services.user_service import get_instance as get_user_service

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

# 获取服务实例
user_service = get_user_service()

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': '缺少用户名或密码'
        }), 400
    
    username = data['username']
    password = data['password']
    
    success, msg, user = user_service.authenticate(username, password)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 401
    
    # 创建会话
    session_id = user_service.create_session(user.id)
    
    # 设置用户会话
    session['user_id'] = user.id
    session['session_id'] = session_id
    
    # Flask-Login登录
    if login_user(user):
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            },
            'session_id': session_id
        })
    
    return jsonify({
        'success': False,
        'message': '登录失败，请稍后重试'
    }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出接口"""
    if 'session_id' in session:
        user_service.logout(session['session_id'])
        
    logout_user()
    session.clear()
    
    return jsonify({
        'success': True,
        'message': '已成功登出'
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'message': '缺少注册信息'
        }), 400
    
    # 检查必要字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段：{field}'
            }), 400
    
    # 从配置获取是否启用注册
    from src.utils import config
    if not config.get("user_management.enable_registration", False):
        return jsonify({
            'success': False,
            'message': '用户注册功能已关闭'
        }), 403
    
    # 创建用户
    success, msg, user = user_service.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name', ''),
        is_admin=False  # 注册的用户默认不是管理员
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '注册成功，请登录',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@auth_bp.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户的个人资料"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'avatar_url': current_user.avatar_url,
            'is_admin': current_user.is_admin,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
    })

@auth_bp.route('/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户个人资料"""
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'message': '缺少更新数据'
        }), 400
    
    # 允许更新的字段
    allowed_fields = {'email', 'full_name', 'avatar_url'}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({
            'success': False,
            'message': '没有可更新的字段'
        }), 400
    
    success, msg = user_service.update_user(current_user.id, **update_data)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '个人资料已更新'
    })

@auth_bp.route('/user/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.json
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({
            'success': False,
            'message': '缺少当前密码或新密码'
        }), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    success, msg = user_service.change_password(
        current_user.id, current_password, new_password)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '密码已成功修改'
    })

@auth_bp.route('/user/api-keys', methods=['GET'])
@login_required
def list_api_keys():
    """获取用户API密钥列表"""
    keys = user_service.list_api_keys(current_user.id)
    
    return jsonify({
        'success': True,
        'api_keys': [key.to_dict() for key in keys]
    })

@auth_bp.route('/user/api-keys', methods=['POST'])
@login_required
def create_api_key():
    """创建新的API密钥"""
    data = request.json
    
    if not data or 'key_name' not in data:
        return jsonify({
            'success': False,
            'message': '缺少API密钥名称'
        }), 400
    
    key_name = data['key_name']
    permissions = data.get('permissions', [])
    expires_days = data.get('expires_days', None)
    
    success, msg, api_key = user_service.create_api_key(
        current_user.id, key_name, permissions, expires_days)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '已创建API密钥',
        'api_key': api_key  # 这是完整的密钥，仅在创建时返回一次
    })

@auth_bp.route('/user/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def revoke_api_key(key_id):
    """撤销API密钥"""
    success, msg = user_service.revoke_api_key(key_id, current_user.id)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '已撤销API密钥'
    })

# 管理员专用接口
@auth_bp.route('/admin/users', methods=['GET'])
@login_required
def list_users():
    """获取用户列表（管理员）"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': '需要管理员权限'
        }), 403
    
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    query = request.args.get('query', '')
    
    users = user_service.list_users(offset, limit, query)
    
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users],
        'pagination': {
            'offset': offset,
            'limit': limit,
            'total': len(users)  # 这里简化处理，实际应获取总数
        }
    })

@auth_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情（管理员）"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': '需要管理员权限'
        }), 403
    
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """更新用户信息（管理员）"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': '需要管理员权限'
        }), 403
    
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'message': '缺少更新数据'
        }), 400
    
    success, msg = user_service.update_user(user_id, **data)
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '用户信息已更新'
    })

@auth_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    """重置用户密码（管理员）"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': '需要管理员权限'
        }), 403
    
    data = request.json
    
    if not data or 'new_password' not in data:
        return jsonify({
            'success': False,
            'message': '缺少新密码'
        }), 400
    
    success, msg = user_service.reset_password(user_id, data['new_password'])
    
    if not success:
        return jsonify({
            'success': False,
            'message': msg
        }), 400
    
    return jsonify({
        'success': True,
        'message': '密码已重置'
    }) 