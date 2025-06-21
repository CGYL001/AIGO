import os
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, session

from src.utils import config, logger, hardware_info
from src.services import ModelServiceFactory, model_manager, auth_service
from src.modules.knowledge_base import KnowledgeBase
from src.modules.code_completion import CodeCompletion
from src.modules.error_checker import ErrorChecker
from src.modules.code_analyzer import CodeAnalyzer
from src.modules.repo_integration import RepoManager
from src.services.repo_permission_service import get_instance as get_repo_permission_service

# 创建Flask应用
app = Flask(
    __name__,
    template_folder=Path(__file__).parent.parent / "templates",
    static_folder=Path(__file__).parent.parent / "static"
)

# 初始化服务和模块
model_service = ModelServiceFactory.create_service()
knowledge_base = KnowledgeBase(embedding_model=config.get("models.embedding.name", "bge-m3"))
code_completion = CodeCompletion(model_name=config.get("models.inference.name", "codellama:7b-instruct-q4_K_M"))
error_checker = ErrorChecker()
code_analyzer = CodeAnalyzer()
repo_manager = RepoManager()

# 资源监控实例
resource_monitor = None

@app.route('/')
def index():
    """首页"""
    return render_template('index.html', 
                         app_name=config.get("app.name", "CodeAssistant"),
                         version=config.get("app.version", "0.1.0"))

@app.route('/models')
def models_page():
    """模型管理页面"""
    # 获取硬件信息
    hw_info = hardware_info.get_hardware_info()
    
    # 获取可用模型
    available_models = model_manager.get_available_models()
    for model in available_models:
        # 检查模型是否适合当前硬件
        model['is_compatible'] = model_manager._check_hardware_compatibility(model.get('name', ''))

    # 获取已加载模型
    loaded_models = list(model_manager._loaded_models)
    
    # 获取系统资源监控数据
    system_info = resource_monitor.get_system_info() if resource_monitor else None
    recommended_models = resource_monitor.get_recommended_models() if resource_monitor else None
    running_mode = resource_monitor.running_mode if resource_monitor else "未知"
    
    return render_template('models.html',
                         app_name=config.get("app.name", "CodeAssistant"),
                         version=config.get("app.version", "0.1.0"),
                         hardware_info=hw_info,
                         system_info=system_info,
                         recommended_models=recommended_models,
                         running_mode=running_mode,
                         available_models=available_models,
                         loaded_models=loaded_models)

@app.route('/repository')
def repository_page():
    """仓库管理页面"""
    # 获取支持的平台
    platforms = repo_manager.get_platforms()
    
    # 获取本地仓库列表
    local_repos = repo_manager.get_local_repositories()
    
    # 获取权限模式
    auth_mode = "strict"  # 默认严格模式
    trust_status = {
        "mode": "strict",
        "trusted": False,
        "confirm_count": 0,
        "required_count": 3
    }
    
    # 如果有会话ID，获取实际权限状态
    if 'auth_session_id' in session:
        auth_mode = auth_service.get_instance().get_current_mode(session['auth_session_id'])
        trust_status = auth_service.get_instance().get_trust_status(session['auth_session_id'])
    
    return render_template('repository.html',
                         app_name=config.get("app.name", "CodeAssistant"),
                         version=config.get("app.version", "0.1.0"),
                         platforms=platforms,
                         local_repos=local_repos,
                         auth_mode=auth_mode,
                         trust_status=trust_status)

@app.route('/api/completion', methods=['POST'])
def code_completion_api():
    """代码补全API"""
    data = request.get_json()
    code_context = data.get('code', '')
    language = data.get('language', 'python')
    cursor_position = data.get('cursor_position')
    max_tokens = data.get('max_tokens', 100)
    
    completion = code_completion.complete(
        code_context, 
        language=language, 
        max_tokens=max_tokens, 
        cursor_position=cursor_position
    )
    
    return jsonify({
        'completion': completion
    })

@app.route('/api/check_code', methods=['POST'])
def check_code_api():
    """代码检查API"""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    issues = error_checker.check(code, language=language)
    
    return jsonify({
        'issues': issues
    })

@app.route('/api/analyze_code', methods=['POST'])
def analyze_code_api():
    """代码分析API"""
    data = request.get_json()
    file_path = data.get('file_path', '')
    
    if not file_path:
        return jsonify({'error': '未提供文件路径'}), 400
        
    analysis = code_analyzer.analyze_file(file_path)
    
    return jsonify(analysis)

@app.route('/api/analyze_project', methods=['POST'])
def analyze_project_api():
    """项目分析API"""
    data = request.get_json()
    project_dir = data.get('project_dir', '')
    exclude_dirs = data.get('exclude_dirs', [])
    
    if not project_dir:
        return jsonify({'error': '未提供项目目录'}), 400
        
    analysis = code_analyzer.analyze_project(project_dir, exclude_dirs)
    
    return jsonify(analysis)

@app.route('/api/knowledge_base/search', methods=['POST'])
def knowledge_search_api():
    """知识库搜索API"""
    data = request.get_json()
    query = data.get('query', '')
    top_k = data.get('top_k', 5)
    
    if not query:
        return jsonify({'error': '未提供查询内容'}), 400
        
    results = knowledge_base.search(query, top_k=top_k)
    
    return jsonify({
        'results': results
    })

@app.route('/api/knowledge_base/add', methods=['POST'])
def knowledge_add_api():
    """添加知识到知识库API"""
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            # 保存上传的文件
            temp_path = Path('data') / 'uploads' / file.filename
            os.makedirs(temp_path.parent, exist_ok=True)
            file.save(temp_path)
            
            # 添加到知识库
            success = knowledge_base.add_document(str(temp_path))
            
            return jsonify({
                'success': success,
                'file': file.filename
            })
    elif request.is_json:
        data = request.get_json()
        text = data.get('text', '')
        metadata = data.get('metadata', {})
        
        if text:
            success = knowledge_base.add_text(text, metadata)
            return jsonify({
                'success': success
            })
            
    return jsonify({'error': '无效的请求'}), 400

@app.route('/api/models/load', methods=['POST'])
def load_model_api():
    """加载模型API"""
    data = request.get_json()
    model_name = data.get('model_name')
    
    if not model_name:
        return jsonify({'success': False, 'error': '未提供模型名称'}), 400
        
    try:
        success = model_manager._load_model(model_name)
        return jsonify({
            'success': success,
            'message': f'模型 {model_name} 加载{"成功" if success else "失败"}'
        })
    except Exception as e:
        logger.error(f"加载模型API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/unload', methods=['POST'])
def unload_model_api():
    """卸载模型API"""
    data = request.get_json()
    model_name = data.get('model_name')
    
    if not model_name:
        return jsonify({'success': False, 'error': '未提供模型名称'}), 400
    
    try:
        model_manager._unload_model(model_name)
        return jsonify({
            'success': True,
            'message': f'模型 {model_name} 已卸载'
        })
    except Exception as e:
        logger.error(f"卸载模型API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/test', methods=['POST'])
def test_model_api():
    """测试模型API"""
    data = request.get_json()
    model_name = data.get('model_name')
    
    if not model_name:
        return jsonify({'success': False, 'error': '未提供模型名称'}), 400
        
    try:
        start_time = time.time()
        service = model_manager.get_model_service(model_name)
        output = service.generate(
            "请用一句话告诉我，你是什么模型?", 
            model=model_name,
            max_tokens=50
        )
        response_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
        
        return jsonify({
            'success': True,
            'output': output,
            'response_time': response_time
        })
    except Exception as e:
        logger.error(f"测试模型API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/hardware', methods=['GET'])
def hardware_info_api():
    """获取硬件信息API"""
    try:
        hw_info = hardware_info.get_hardware_info(force_update=True)
        return jsonify({
            'success': True,
            'data': hw_info
        })
    except Exception as e:
        logger.error(f"获取硬件信息API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/resources', methods=['GET'])
def system_resources_api():
    """获取系统资源监控信息API"""
    try:
        if not resource_monitor:
            return jsonify({
                'success': False,
                'error': '系统资源监控未启用'
            }), 404
            
        system_info = resource_monitor.get_system_info()
        recommended_models = resource_monitor.get_recommended_models()
        
        return jsonify({
            'success': True,
            'system_info': system_info,
            'recommended_models': recommended_models,
            'running_mode': resource_monitor.running_mode
        })
    except Exception as e:
        logger.error(f"获取系统资源监控API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/system/set_mode', methods=['POST'])
def set_system_mode_api():
    """设置系统运行模式API"""
    try:
        if not resource_monitor:
            return jsonify({
                'success': False,
                'error': '系统资源监控未启用'
            }), 404
            
        data = request.get_json()
        mode = data.get('mode')
        
        if mode not in ['balanced', 'performance']:
            return jsonify({
                'success': False,
                'error': f'无效的运行模式: {mode}'
            }), 400
            
        success = resource_monitor.set_mode(mode)
        
        # 如果配置为自动推荐模型，则应用推荐结果
        if success and config.get("system_monitor.auto_recommend_models", True):
            recommended_models = resource_monitor.get_recommended_models()
            
            if recommended_models.get("inference"):
                inference_model = recommended_models["inference"]["name"]
                config.set("models.inference.name", inference_model)
                logger.info(f"已将推理模型设置为系统推荐的: {inference_model}")
                # 更新代码补全模块的模型
                code_completion.set_model_name(inference_model)
                
            if recommended_models.get("embedding"):
                embedding_model = recommended_models["embedding"]["name"]
                config.set("models.embedding.name", embedding_model)
                logger.info(f"已将嵌入模型设置为系统推荐的: {embedding_model}")
                # 更新知识库模块的模型
                knowledge_base.set_embedding_model(embedding_model)
        
        return jsonify({
            'success': success,
            'running_mode': resource_monitor.running_mode if success else None,
            'recommended_models': resource_monitor.get_recommended_models() if success else None
        })
    except Exception as e:
        logger.error(f"设置系统运行模式API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/system/check_resources', methods=['POST'])
def check_resources_api():
    """手动触发系统资源检测API"""
    try:
        if not resource_monitor:
            return jsonify({
                'success': False,
                'error': '系统资源监控未启用'
            }), 404
            
        system_info = resource_monitor.check_system()
        
        return jsonify({
            'success': True,
            'system_info': system_info,
            'recommended_models': resource_monitor.get_recommended_models()
        })
    except Exception as e:
        logger.error(f"手动触发系统资源检测API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 仓库管理API
@app.route('/api/repository/platforms', methods=['GET'])
def get_platforms_api():
    """获取支持的代码托管平台列表"""
    platforms = repo_manager.get_platforms()
    
    platforms_info = {}
    for platform in platforms:
        platforms_info[platform] = repo_manager.get_platform_info(platform)
    
    return jsonify({
        'success': True,
        'platforms': platforms_info
    })

@app.route('/api/repository/authenticate', methods=['POST'])
def authenticate_platform_api():
    """认证代码托管平台"""
    data = request.get_json()
    platform = data.get('platform')
    credentials = data.get('credentials', {})
    
    if not platform:
        return jsonify({'success': False, 'error': '未提供平台名称'}), 400
        
    if not repo_manager.is_platform_supported(platform):
        return jsonify({'success': False, 'error': f'不支持的平台: {platform}'}), 400
    
    try:
        # 使用同步方式调用异步函数
        import asyncio
        success, message = asyncio.run(repo_manager.authenticate(platform, credentials))
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"认证平台API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/list', methods=['POST'])
def list_repositories_api():
    """获取仓库列表"""
    data = request.get_json()
    platform = data.get('platform')
    username = data.get('username')
    
    if not platform:
        return jsonify({'success': False, 'error': '未提供平台名称'}), 400
        
    if not repo_manager.is_platform_supported(platform):
        return jsonify({'success': False, 'error': f'不支持的平台: {platform}'}), 400
    
    try:
        # 使用同步方式调用异步函数
        import asyncio
        repos = asyncio.run(repo_manager.list_repositories(platform, username))
        
        return jsonify({
            'success': True,
            'repositories': repos
        })
    except Exception as e:
        logger.error(f"获取仓库列表API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/local', methods=['GET'])
def get_local_repositories_api():
    """获取本地仓库列表"""
    try:
        repos = repo_manager.get_local_repositories()
        
        return jsonify({
            'success': True,
            'repositories': repos
        })
    except Exception as e:
        logger.error(f"获取本地仓库列表API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/clone', methods=['POST'])
def clone_repository_api():
    """克隆仓库"""
    data = request.get_json()
    platform = data.get('platform')
    repo_name = data.get('repo_name')
    branch = data.get('branch')
    
    if not platform or not repo_name:
        return jsonify({'success': False, 'error': '缺少必要参数'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        # 使用同步方式调用异步函数
        import asyncio
        success, message = asyncio.run(repo_manager.clone_repository(platform, repo_name, branch))
        
        # 如果需要确认权限
        if not success and "需要确认" in message:
            return jsonify({
                'success': False,
                'need_confirmation': True,
                'operation': 'repo_clone',
                'message': message
            })
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"克隆仓库API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/pull', methods=['POST'])
def pull_repository_api():
    """拉取仓库更新"""
    data = request.get_json()
    repo_path = data.get('repo_path')
    branch = data.get('branch')
    
    if not repo_path:
        return jsonify({'success': False, 'error': '未提供仓库路径'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        # 使用同步方式调用异步函数
        import asyncio
        success, message = asyncio.run(repo_manager.pull_repository(repo_path, branch))
        
        # 如果需要确认权限
        if not success and "需要确认" in message:
            return jsonify({
                'success': False,
                'need_confirmation': True,
                'operation': 'repo_pull',
                'message': message
            })
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"拉取仓库更新API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/push', methods=['POST'])
def push_repository_api():
    """推送仓库更改"""
    data = request.get_json()
    repo_path = data.get('repo_path')
    message = data.get('message')
    branch = data.get('branch')
    
    if not repo_path or not message:
        return jsonify({'success': False, 'error': '缺少必要参数'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        # 使用同步方式调用异步函数
        import asyncio
        success, result_message = asyncio.run(repo_manager.push_repository(repo_path, message, branch))
        
        # 如果需要确认权限
        if not success and "需要确认" in result_message:
            return jsonify({
                'success': False,
                'need_confirmation': True,
                'operation': 'repo_push',
                'message': result_message
            })
        
        return jsonify({
            'success': success,
            'message': result_message
        })
    except Exception as e:
        logger.error(f"推送仓库更改API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/delete', methods=['POST'])
def delete_repository_api():
    """删除本地仓库"""
    data = request.get_json()
    repo_path = data.get('repo_path')
    
    if not repo_path:
        return jsonify({'success': False, 'error': '未提供仓库路径'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        success, message = repo_manager.delete_local_repository(repo_path)
        
        # 如果需要确认权限
        if not success and "需要确认" in message:
            return jsonify({
                'success': False,
                'need_confirmation': True,
                'operation': 'repo_delete',
                'message': message
            })
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"删除本地仓库API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 仓库权限管理API
@app.route('/api/repository/permissions', methods=['GET'])
def get_repo_permissions_api():
    """获取仓库权限信息"""
    repo_path = request.args.get('repo_path')
    
    if not repo_path:
        return jsonify({'success': False, 'error': '未提供仓库路径'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        permissions = repo_manager.get_repo_permissions(repo_path)
        
        # 获取预定义角色列表
        permission_service = get_repo_permission_service()
        
        return jsonify({
            'success': True,
            'permissions': permissions,
            'available_roles': permission_service.ROLES
        })
    except Exception as e:
        logger.error(f"获取仓库权限API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/protection', methods=['POST'])
def update_repo_protection_api():
    """更新仓库保护规则"""
    data = request.get_json()
    repo_path = data.get('repo_path')
    rules = data.get('rules', {})
    
    if not repo_path:
        return jsonify({'success': False, 'error': '未提供仓库路径'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        success, message = repo_manager.update_repo_protection(repo_path, rules)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"更新仓库保护规则API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/repository/role', methods=['POST'])
def update_user_role_api():
    """更新用户角色"""
    data = request.get_json()
    repo_path = data.get('repo_path')
    user_id = data.get('user_id')
    role = data.get('role')
    
    if not repo_path or not user_id or not role:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    # 设置仓库管理器的会话ID
    repo_manager.set_session(session['auth_session_id'])
    
    try:
        success, message = repo_manager.update_user_role(repo_path, user_id, role)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"更新用户角色API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/audit', methods=['GET'])
def get_repo_audit_logs_api():
    """获取仓库审计日志"""
    repo_path = request.args.get('repo_path')
    limit = request.args.get('limit', 100, type=int)
    
    if not repo_path:
        return jsonify({'success': False, 'error': '未提供仓库路径'}), 400
    
    # 确保会话ID存在
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    try:
        # 获取仓库ID
        permission_service = get_repo_permission_service()
        repo_id = permission_service.generate_repo_id(repo_path)
        
        # 获取审计日志
        logs = permission_service.get_audit_logs(repo_id, limit)
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        logger.error(f"获取仓库审计日志API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 权限管理API
@app.route('/api/auth/session', methods=['POST'])
def create_auth_session_api():
    """创建权限会话"""
    # 创建新的会话
    session_id = auth_service.get_instance().create_session()
    session['auth_session_id'] = session_id
    
    return jsonify({
        'success': True,
        'session_id': session_id
    })

@app.route('/api/auth/status', methods=['GET'])
def get_auth_status_api():
    """获取权限状态"""
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    session_id = session['auth_session_id']
    
    # 获取会话信息
    session_info = auth_service.get_instance().get_session(session_id)
    
    # 获取权限模式
    mode = auth_service.get_instance().get_current_mode(session_id)
    
    # 获取信任状态
    trust_status = auth_service.get_instance().get_trust_status(session_id)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'mode': mode,
        'trust_status': trust_status,
        'session_info': session_info
    })

@app.route('/api/auth/mode', methods=['POST'])
def set_auth_mode_api():
    """设置权限模式"""
    data = request.get_json()
    mode = data.get('mode')
    
    if not mode or mode not in ['strict', 'trust']:
        return jsonify({'success': False, 'error': '无效的权限模式'}), 400
    
    if 'auth_session_id' not in session:
        session['auth_session_id'] = auth_service.get_instance().create_session()
    
    session_id = session['auth_session_id']
    
    # 设置权限模式
    success = auth_service.get_instance().set_session_mode(session_id, mode)
    
    return jsonify({
        'success': success,
        'message': f"已切换到{mode}模式" if success else "切换模式失败"
    })

@app.route('/api/auth/confirm', methods=['POST'])
def confirm_operation_api():
    """确认操作"""
    data = request.get_json()
    operation = data.get('operation')
    
    if not operation:
        return jsonify({'success': False, 'error': '未提供操作类型'}), 400
    
    if 'auth_session_id' not in session:
        return jsonify({'success': False, 'error': '无效的会话'}), 400
    
    session_id = session['auth_session_id']
    
    # 确认操作
    success = auth_service.get_instance().confirm_operation(session_id, operation)
    
    # 获取更新后的信任状态
    trust_status = auth_service.get_instance().get_trust_status(session_id)
    
    return jsonify({
        'success': success,
        'message': "操作已确认" if success else "确认操作失败",
        'trust_status': trust_status
    })

def start_web_app(host: str = None, port: int = None, debug: bool = None, system_monitor = None):
    """启动Web应用"""
    global resource_monitor
    
    # 初始化必要的目录结构
    from src.utils.init_utils import ensure_directories
    ensure_directories()
    
    # 设置host和port
    if host is None:
        host = config.get("app.host", "localhost")
    if port is None:
        port = config.get("app.port", 8080)
    if debug is None:
        debug = config.get("app.debug", False)
        
    # 设置资源监控
    resource_monitor = system_monitor
    
    # 设置会话密钥
    app.secret_key = os.urandom(24)
    
    # 确保会话目录存在
    os.makedirs('instance', exist_ok=True)
    
    # 检查模型服务状态
    model_available = _check_model_service()
    if not model_available:
        logger.warning("模型服务不可用，某些功能将被禁用")
    
    # 注入会话管理中间件
    @app.before_request
    def before_request():
        # 确保每个会话都有一个唯一的身份验证会话ID
        if 'auth_session_id' not in session:
            session['auth_session_id'] = auth_service.get_instance().create_session()
        
        # 设置仓库管理器会话ID
        repo_manager.set_session(session.get('auth_session_id'))
    
    # 注册错误处理器
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="页面未找到"), 404
                             
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', 
                             error_code=500, 
                             error_message="服务器内部错误"), 500
    
    # 启动服务器
    logger.info(f"启动Web服务器 http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

def _check_model_service():
    """检查模型服务状态"""
    try:
        return model_service.is_available()
    except Exception as e:
        logger.error(f"检查模型服务失败: {str(e)}")
        return False

if __name__ == '__main__':
    start_web_app() 