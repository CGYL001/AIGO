"""
仓库权限管理相关的API路由
"""

import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user

from src.services.repo_permission_service import get_instance as get_repo_permission_service
from src.services.user_service import get_instance as get_user_service

logger = logging.getLogger(__name__)
repo_permission_bp = Blueprint('repo_permission', __name__)

# 获取服务实例
repo_permission_service = get_repo_permission_service()
user_service = get_user_service()

@repo_permission_bp.route('/repositories/<repo_id>/permissions/users', methods=['GET'])
@login_required
def list_user_permissions(repo_id):
    """
    获取仓库的用户权限列表
    """
    # 检查当前用户是否有权限查看
    user_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if user_role not in ["admin"]:
        return jsonify({
            'success': False,
            'message': '没有权限查看仓库用户权限列表'
        }), 403
    
    permissions = repo_permission_service.list_user_permissions(repo_id)
    
    return jsonify({
        'success': True,
        'permissions': permissions
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/teams', methods=['GET'])
@login_required
def list_team_permissions(repo_id):
    """
    获取仓库的团队权限列表
    """
    # 检查当前用户是否有权限查看
    user_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if user_role not in ["admin"]:
        return jsonify({
            'success': False,
            'message': '没有权限查看仓库团队权限列表'
        }), 403
    
    permissions = repo_permission_service.list_team_permissions(repo_id)
    
    return jsonify({
        'success': True,
        'permissions': permissions
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/users/<int:user_id>', methods=['PUT'])
@login_required
def assign_user_role(repo_id, user_id):
    """
    分配用户在仓库中的角色
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限修改用户角色'
        }), 403
    
    data = request.json
    if not data or 'role' not in data:
        return jsonify({
            'success': False,
            'message': '缺少角色信息'
        }), 400
    
    role = data['role']
    if role not in repo_permission_service.ROLES:
        return jsonify({
            'success': False,
            'message': f'无效的角色: {role}'
        }), 400
    
    # 检查目标用户是否存在
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        return jsonify({
            'success': False,
            'message': f'用户ID {user_id} 不存在'
        }), 404
    
    # 分配角色
    success = repo_permission_service.assign_role(repo_id, user_id, role)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '角色分配失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已将用户 {target_user.username} 的角色设置为 {role}'
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/users/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user_role(repo_id, user_id):
    """
    移除用户在仓库中的角色
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限移除用户角色'
        }), 403
    
    # 检查目标用户是否存在
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        return jsonify({
            'success': False,
            'message': f'用户ID {user_id} 不存在'
        }), 404
    
    # 移除角色
    success = repo_permission_service.remove_user_role(repo_id, user_id)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '角色移除失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已移除用户 {target_user.username} 的角色'
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/teams/<int:team_id>', methods=['PUT'])
@login_required
def assign_team_role(repo_id, team_id):
    """
    分配团队在仓库中的角色
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限修改团队角色'
        }), 403
    
    data = request.json
    if not data or 'role' not in data:
        return jsonify({
            'success': False,
            'message': '缺少角色信息'
        }), 400
    
    role = data['role']
    if role not in repo_permission_service.ROLES:
        return jsonify({
            'success': False,
            'message': f'无效的角色: {role}'
        }), 400
    
    # 分配角色
    success = repo_permission_service.assign_team_role(repo_id, team_id, role)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '团队角色分配失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已将团队ID {team_id} 的角色设置为 {role}'
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/teams/<int:team_id>', methods=['DELETE'])
@login_required
def remove_team_role(repo_id, team_id):
    """
    移除团队在仓库中的角色
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限移除团队角色'
        }), 403
    
    # 移除角色
    success = repo_permission_service.remove_team_role(repo_id, team_id)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '团队角色移除失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已移除团队ID {team_id} 的角色'
    })

@repo_permission_bp.route('/repositories/<repo_id>/permissions/custom', methods=['PUT'])
@login_required
def set_custom_permission(repo_id):
    """
    设置用户自定义权限
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限设置自定义权限'
        }), 403
    
    data = request.json
    if not data or 'user_id' not in data or 'operation' not in data or 'granted' not in data:
        return jsonify({
            'success': False,
            'message': '缺少必要参数'
        }), 400
    
    user_id = data['user_id']
    operation = data['operation']
    granted = data['granted']
    
    if operation not in repo_permission_service.OPERATIONS:
        return jsonify({
            'success': False,
            'message': f'无效的操作类型: {operation}'
        }), 400
    
    # 设置自定义权限
    success = repo_permission_service.set_custom_permission(repo_id, user_id, operation, granted)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '设置自定义权限失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已{"授予" if granted else "移除"}用户ID {user_id} 的 {operation} 权限'
    })

@repo_permission_bp.route('/repositories/<repo_id>/protection_rules', methods=['GET'])
@login_required
def get_protection_rules(repo_id):
    """
    获取仓库的保护规则
    """
    # 任何有权访问仓库的用户都可以查看保护规则
    user_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if user_role not in ["admin", "developer", "reader"]:
        return jsonify({
            'success': False,
            'message': '没有权限查看仓库保护规则'
        }), 403
    
    rules = repo_permission_service.get_protection_rules(repo_id)
    
    return jsonify({
        'success': True,
        'rules': rules
    })

@repo_permission_bp.route('/repositories/<repo_id>/protection_rules', methods=['PUT'])
@login_required
def set_protection_rule(repo_id):
    """
    设置仓库保护规则
    """
    # 检查当前用户是否有权限修改
    current_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if current_role != "admin":
        return jsonify({
            'success': False,
            'message': '没有权限修改保护规则'
        }), 403
    
    data = request.json
    if not data or 'rule_type' not in data:
        return jsonify({
            'success': False,
            'message': '缺少规则类型'
        }), 400
    
    rule_type = data['rule_type']
    enabled = data.get('enabled')
    target = data.get('target')
    config = data.get('config')
    
    if rule_type not in repo_permission_service.RULE_TYPES:
        return jsonify({
            'success': False,
            'message': f'无效的规则类型: {rule_type}'
        }), 400
    
    # 设置规则
    success = repo_permission_service.set_protection_rule(
        repo_id, rule_type, enabled, target, config)
    
    if not success:
        return jsonify({
            'success': False,
            'message': '设置保护规则失败'
        }), 500
    
    return jsonify({
        'success': True,
        'message': f'已更新{repo_permission_service.RULE_TYPES[rule_type]}规则'
    })

@repo_permission_bp.route('/repositories/<repo_id>/audit_logs', methods=['GET'])
@login_required
def get_audit_logs(repo_id):
    """
    获取仓库的审计日志
    """
    # 检查当前用户是否有权限查看
    user_role = repo_permission_service.get_user_role(repo_id, current_user.id)
    if user_role not in ["admin"]:
        return jsonify({
            'success': False,
            'message': '没有权限查看审计日志'
        }), 403
    
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    logs = repo_permission_service.get_audit_logs(repo_id, limit, offset)
    
    return jsonify({
        'success': True,
        'logs': logs
    })

@repo_permission_bp.route('/repositories/<repo_id>/user_role', methods=['GET'])
@login_required
def get_current_user_role(repo_id):
    """
    获取当前用户在仓库中的角色
    """
    role = repo_permission_service.get_user_role(repo_id, current_user.id)
    
    return jsonify({
        'success': True,
        'role': role,
        'permissions': repo_permission_service.ROLES.get(role, {}).get('permissions', [])
    }) 