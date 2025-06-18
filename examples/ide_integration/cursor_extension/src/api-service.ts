import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

/**
 * AIgo API服务类
 * 处理与AIgo服务器的所有API通信
 */
export class AIgoApiService {
    private axiosInstance: AxiosInstance;
    private baseUrl: string;
    private authToken: string;

    constructor(baseUrl: string, authToken: string = '') {
        this.baseUrl = baseUrl;
        this.authToken = authToken;

        // 创建axios实例
        this.axiosInstance = axios.create({
            baseURL: baseUrl,
            timeout: 30000, // 30秒超时
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // 请求拦截器
        this.axiosInstance.interceptors.request.use(config => {
            if (this.authToken) {
                config.headers['Authorization'] = `Bearer ${this.authToken}`;
            }
            return config;
        });

        // 响应拦截器
        this.axiosInstance.interceptors.response.use(
            response => response,
            error => {
                console.error('API请求错误:', error);
                return Promise.reject(error);
            }
        );
    }

    /**
     * 更新配置
     */
    public updateConfig(baseUrl: string, authToken: string) {
        this.baseUrl = baseUrl;
        this.authToken = authToken;
        this.axiosInstance.defaults.baseURL = baseUrl;
    }

    /**
     * 检查服务器状态
     */
    public async checkStatus(): Promise<boolean> {
        try {
            const response = await this.axiosInstance.get('/status');
            return response.status === 200;
        } catch (error) {
            console.error('服务器状态检查失败:', error);
            return false;
        }
    }

    /**
     * 扫描文件系统
     */
    public async scanFileSystem(path: string): Promise<any> {
        try {
            const response = await this.axiosInstance.post('/filesystem/scan', { path });
            return response.data;
        } catch (error) {
            console.error('文件系统扫描失败:', error);
            throw error;
        }
    }

    /**
     * 创建上下文
     */
    public async createContext(name: string, content: string, type: string): Promise<any> {
        try {
            const response = await this.axiosInstance.post('/context/create', {
                name,
                content,
                type
            });
            return response.data;
        } catch (error) {
            console.error('创建上下文失败:', error);
            throw error;
        }
    }

    /**
     * 获取上下文列表
     */
    public async getContextList(): Promise<any> {
        try {
            const response = await this.axiosInstance.get('/context/list');
            return response.data;
        } catch (error) {
            console.error('获取上下文列表失败:', error);
            throw error;
        }
    }

    /**
     * 切换模型
     */
    public async switchModel(useLocalModel: boolean): Promise<any> {
        try {
            const response = await this.axiosInstance.post('/model/switch', {
                useLocalModel
            });
            return response.data;
        } catch (error) {
            console.error('切换模型失败:', error);
            throw error;
        }
    }

    /**
     * 生成代码
     */
    public async generateCode(prompt: string, language: string, contextIds: string[] = []): Promise<any> {
        try {
            const response = await this.axiosInstance.post('/model/generate', {
                prompt,
                language,
                contextIds
            });
            return response.data;
        } catch (error) {
            console.error('代码生成失败:', error);
            throw error;
        }
    }

    /**
     * 分析代码
     */
    public async analyzeCode(code: string, language: string): Promise<any> {
        try {
            const response = await this.axiosInstance.post('/code/analyze', {
                code,
                language
            });
            return response.data;
        } catch (error) {
            console.error('代码分析失败:', error);
            throw error;
        }
    }

    /**
     * 获取模型列表
     */
    public async getModelList(): Promise<any> {
        try {
            const response = await this.axiosInstance.get('/model/list');
            return response.data;
        } catch (error) {
            console.error('获取模型列表失败:', error);
            throw error;
        }
    }
}
