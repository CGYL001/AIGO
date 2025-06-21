import http.server
import socketserver
import json
import subprocess
import os
from urllib.parse import parse_qs, urlparse

PORT = 8080

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # 使用字符串而不是bytes，并在写入时编码
            html_content = """
            <html>
            <head>
                <title>AIgo Server - Model Manager</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                </style>
            </head>
            <body>
                <h1>AIgo Model Manager</h1>
                <div>
                    <h2>Available API endpoints</h2>
                    <ul>
                        <li><a href="/api/status">/api/status</a> - Server status</li>
                        <li><a href="/api/models">/api/models</a> - Get model list</li>
                        <li><a href="/api/current">/api/current</a> - Get current config</li>
                        <li><code>/api/switch?model=MODEL_NAME</code> - Switch model</li>
                        <li><code>/api/optimize?temperature=0.2&max_tokens=2048</code> - Optimize parameters</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'ok',
                'version': '0.2.0',
                'message': 'AIgo API server running'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif path == '/api/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Call model_manager.py list command
            try:
                result = subprocess.run(['python', 'model_manager.py', 'list'], 
                                      capture_output=True, text=True)
                
                # Parse output to extract model info
                models = []
                for line in result.stdout.splitlines():
                    if line.startswith('- '):
                        parts = line.strip('- ').split('(')
                        if len(parts) >= 2:
                            model_name = parts[0].strip()
                            size_info = parts[1].split(',')[0] if ',' in parts[1] else parts[1]
                            models.append({
                                'name': model_name,
                                'size': size_info
                            })
                
                response = {
                    'status': 'success',
                    'models': models
                }
            except Exception as e:
                response = {
                    'status': 'error',
                    'message': str(e)
                }
                
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif path == '/api/current':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Call model_manager.py show command
            try:
                result = subprocess.run(['python', 'model_manager.py', 'show'], 
                                      capture_output=True, text=True)
                
                # Extract config info
                config = {
                    'raw_output': result.stdout
                }
                
                # Parse key info from output
                for line in result.stdout.splitlines():
                    if 'model:' in line.lower():
                        config['model'] = line.split(':')[1].strip()
                    elif 'provider:' in line.lower():
                        config['provider'] = line.split(':')[1].strip()
                    elif 'api' in line.lower() and 'address:' in line.lower():
                        config['api_base'] = line.split(':')[1].strip()
                    elif 'temperature:' in line.lower():
                        config['temperature'] = line.split(':')[1].strip()
                    elif 'max' in line.lower() and 'tokens:' in line.lower():
                        config['max_tokens'] = line.split(':')[1].strip()
                    elif 'context' in line.lower() and 'length:' in line.lower():
                        config['max_context_length'] = line.split(':')[1].strip()
                
                response = {
                    'status': 'success',
                    'config': config
                }
            except Exception as e:
                response = {
                    'status': 'error',
                    'message': str(e)
                }
                
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif path.startswith('/api/switch'):
            # Parse query parameters
            query = parse_qs(urlparse(self.path).query)
            model_name = query.get('model', [''])[0]
            
            if not model_name:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'error',
                    'message': 'Missing model parameter'
                }
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Call model_manager.py switch command
                try:
                    result = subprocess.run(['python', 'model_manager.py', 'switch', model_name], 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        response = {
                            'status': 'success',
                            'message': f'Successfully switched to model: {model_name}',
                            'output': result.stdout
                        }
                    else:
                        response = {
                            'status': 'error',
                            'message': 'Failed to switch model',
                            'error': result.stderr
                        }
                except Exception as e:
                    response = {
                        'status': 'error',
                        'message': str(e)
                    }
                    
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif path.startswith('/api/optimize'):
            # Parse query parameters
            query = parse_qs(urlparse(self.path).query)
            temperature = query.get('temperature', [''])[0]
            max_tokens = query.get('max_tokens', [''])[0]
            timeout = query.get('timeout', [''])[0]
            context_length = query.get('context_length', [''])[0]
            
            command = ['python', 'model_manager.py', 'optimize']
            if temperature:
                command.extend(['--temperature', temperature])
            if max_tokens:
                command.extend(['--max-tokens', max_tokens])
            if timeout:
                command.extend(['--timeout', timeout])
            if context_length:
                command.extend(['--context-length', context_length])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Call model_manager.py optimize command
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                
                if result.returncode == 0:
                    response = {
                        'status': 'success',
                        'message': 'Model parameters optimized successfully',
                        'output': result.stdout
                    }
                else:
                    response = {
                        'status': 'error',
                        'message': 'Failed to optimize model parameters',
                        'error': result.stderr
                    }
            except Exception as e:
                response = {
                    'status': 'error',
                    'message': str(e)
                }
                
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

def run_server():
    handler = MyHandler
    
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"Server started at 0.0.0.0:{PORT}")
        print(f"You can access it from your local machine at: http://localhost:{PORT}")
        print(f"Or from other devices on your network using your IP address")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")

if __name__ == "__main__":
    run_server() 