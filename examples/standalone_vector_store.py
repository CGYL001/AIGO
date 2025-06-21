"""
独立向量存储示例

这个示例展示了分片向量存储的基本功能，不依赖于AIgo项目的其他部分。
"""

import os
import time
import pickle
import threading
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Set, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import tempfile

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    计算两个向量的余弦相似度
    
    Args:
        a: 第一个向量
        b: 第二个向量
        
    Returns:
        余弦相似度，范围为[-1, 1]
    """
    if len(a) != len(b):
        raise ValueError(f"向量维度不匹配: {len(a)} vs {len(b)}")
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # 避免除零错误
    if norm_a == 0 or norm_b == 0:
        return 0
    
    return dot_product / (norm_a * norm_b)


@dataclass
class VectorChunk:
    """向量分块，用于管理向量子集"""
    
    id: str  # 分块ID
    vectors: Dict[str, List[float]] = field(default_factory=dict)  # ID到向量的映射
    metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # ID到元数据的映射
    active: bool = True  # 是否活跃（用于惰性加载）
    last_access: float = field(default_factory=time.time)  # 最后访问时间
    size: int = 0  # 向量数量
    dimension: int = 0  # 向量维度
    
    def add(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加向量到分块"""
        if not self.dimension:
            self.dimension = len(vector)
        elif len(vector) != self.dimension:
            return False
            
        self.vectors[id] = vector
        self.metadata[id] = metadata or {}
        self.size += 1
        self.last_access = time.time()
        return True
    
    def remove(self, id: str) -> bool:
        """从分块中删除向量"""
        if id not in self.vectors:
            return False
            
        del self.vectors[id]
        del self.metadata[id]
        self.size -= 1
        self.last_access = time.time()
        return True
    
    def get(self, id: str) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        """获取向量和元数据"""
        if id not in self.vectors:
            return None
            
        self.last_access = time.time()
        return (self.vectors[id], self.metadata[id])
    
    def search(
        self, 
        query_vector: List[float], 
        limit: int = 10,
        similarity_fn: Callable = cosine_similarity
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """在分块内搜索最相似的向量"""
        if not self.vectors:
            return []
            
        self.last_access = time.time()
        
        # 计算相似度
        results = []
        for id, vector in self.vectors.items():
            try:
                similarity = similarity_fn(query_vector, vector)
                results.append((id, similarity, self.metadata[id]))
            except Exception as e:
                logger.warning(f"计算向量 {id} 的相似度时出错: {e}")
                
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def save(self, path: str) -> bool:
        """保存分块到文件"""
        try:
            with open(path, "wb") as f:
                pickle.dump({
                    "id": self.id,
                    "vectors": self.vectors,
                    "metadata": self.metadata,
                    "dimension": self.dimension,
                    "size": self.size
                }, f)
            return True
        except Exception as e:
            logger.error(f"保存分块失败: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """从文件加载分块"""
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                
            self.vectors = data["vectors"]
            self.metadata = data["metadata"]
            self.dimension = data["dimension"]
            self.size = data["size"]
            self.active = True
            self.last_access = time.time()
            return True
        except Exception as e:
            logger.error(f"加载分块失败: {e}")
            return False
    
    def unload(self) -> bool:
        """卸载分块内容以节省内存"""
        if not self.active:
            return True
            
        self.vectors = {}
        self.metadata = {}
        self.active = False
        return True
    
    def is_empty(self) -> bool:
        """检查分块是否为空"""
        return self.size == 0


class ShardedVectorStore:
    """
    分片向量存储
    
    将向量分散存储在多个分块中，支持并行搜索和惰性加载。
    适用于大规模向量集合和分布式部署。
    """
    
    def __init__(
        self, 
        dimension: int = 1536,
        chunk_size: int = 10000,  # 每个分块的最大向量数
        max_active_chunks: int = 10,  # 同时活跃的最大分块数
        parallelism: int = 4  # 并行度
    ):
        """
        初始化分片向量存储
        
        Args:
            dimension: 向量维度
            chunk_size: 每个分块的最大向量数
            max_active_chunks: 同时活跃的最大分块数
            parallelism: 并行检索的线程数
        """
        self.dimension = dimension
        self.chunk_size = chunk_size
        self.max_active_chunks = max_active_chunks
        self.parallelism = min(parallelism, os.cpu_count() or 4)
        
        self.chunks: Dict[str, VectorChunk] = {}
        self.id_to_chunk: Dict[str, str] = {}  # 向量ID到分块ID的映射
        self.current_chunk_id: str = "chunk_1"
        self.initialized = True
        
        # 线程池用于并行搜索
        self.executor = ThreadPoolExecutor(max_workers=self.parallelism)
        
        # 线程锁用于并发控制
        self.lock = threading.RLock()
        
        # 创建初始分块
        self._create_new_chunk()
    
    def _create_new_chunk(self) -> str:
        """创建新的分块"""
        with self.lock:
            chunk_id = f"chunk_{len(self.chunks) + 1}"
            self.chunks[chunk_id] = VectorChunk(id=chunk_id, dimension=self.dimension)
            self.current_chunk_id = chunk_id
            return chunk_id
    
    def _get_target_chunk(self) -> VectorChunk:
        """获取目标分块用于添加新向量"""
        with self.lock:
            current_chunk = self.chunks[self.current_chunk_id]
            
            # 如果当前分块已满，创建新分块
            if current_chunk.size >= self.chunk_size:
                new_chunk_id = self._create_new_chunk()
                return self.chunks[new_chunk_id]
            
            return current_chunk
    
    def _ensure_chunk_active(self, chunk_id: str) -> bool:
        """确保分块处于活跃状态，如果需要可能会卸载其他分块"""
        with self.lock:
            if chunk_id not in self.chunks:
                return False
                
            chunk = self.chunks[chunk_id]
            
            # 如果已经活跃，直接返回
            if chunk.active:
                chunk.last_access = time.time()
                return True
                
            # 统计活跃分块数
            active_chunks = [c for c in self.chunks.values() if c.active]
            
            # 如果活跃分块数达到上限，卸载最不常用的分块
            if len(active_chunks) >= self.max_active_chunks:
                active_chunks.sort(key=lambda c: c.last_access)
                for old_chunk in active_chunks[:len(active_chunks) - self.max_active_chunks + 1]:
                    old_chunk.unload()
            
            # 激活目标分块
            # 注意：在实际实现中，这里应该从持久化存储加载分块
            chunk.active = True
            chunk.last_access = time.time()
            return True
    
    def add(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加向量到存储"""
        if len(vector) != self.dimension:
            logger.warning(f"向量维度不匹配: 预期 {self.dimension}, 实际 {len(vector)}")
            return False
        
        with self.lock:
            # 如果ID已存在，先删除
            if id in self.id_to_chunk:
                self.delete(id)
            
            # 获取目标分块并添加向量
            chunk = self._get_target_chunk()
            if chunk.add(id, vector, metadata):
                self.id_to_chunk[id] = chunk.id
                return True
            
            return False
    
    def get(self, id: str) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        """获取指定ID的向量"""
        with self.lock:
            if id not in self.id_to_chunk:
                return None
            
            chunk_id = self.id_to_chunk[id]
            
            # 确保分块活跃
            if not self._ensure_chunk_active(chunk_id):
                return None
            
            # 从分块中获取向量
            return self.chunks[chunk_id].get(id)
    
    def search(self, query_vector: List[float], limit: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索最相似的向量（并行实现）"""
        if len(query_vector) != self.dimension:
            logger.warning(f"查询向量维度不匹配: 预期 {self.dimension}, 实际 {len(query_vector)}")
            return []
        
        # 只搜索活跃的分块
        active_chunk_ids = []
        with self.lock:
            for chunk_id, chunk in self.chunks.items():
                if chunk.active and not chunk.is_empty():
                    active_chunk_ids.append(chunk_id)
                elif not chunk.active and chunk.size > 0:
                    # 激活有数据的非活跃分块
                    if self._ensure_chunk_active(chunk_id):
                        active_chunk_ids.append(chunk_id)
        
        if not active_chunk_ids:
            return []
        
        # 并行搜索各个分块
        chunk_futures = {}
        for chunk_id in active_chunk_ids:
            chunk = self.chunks[chunk_id]
            future = self.executor.submit(chunk.search, query_vector, limit * 2)
            chunk_futures[future] = chunk_id
        
        # 收集并合并结果
        all_results = []
        for future in chunk_futures:
            try:
                results = future.result(timeout=5.0)  # 设置超时以防止阻塞
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"搜索分块 {chunk_futures[future]} 时出错: {e}")
        
        # 全局排序
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:limit]
    
    def delete(self, id: str) -> bool:
        """删除向量"""
        with self.lock:
            if id not in self.id_to_chunk:
                return False
            
            chunk_id = self.id_to_chunk[id]
            
            # 确保分块活跃
            if not self._ensure_chunk_active(chunk_id):
                return False
            
            # 从分块中删除向量
            chunk = self.chunks[chunk_id]
            if chunk.remove(id):
                del self.id_to_chunk[id]
                return True
            
            return False
    
    def clear(self) -> int:
        """清空存储"""
        with self.lock:
            count = len(self.id_to_chunk)
            
            # 清空所有分块
            for chunk in self.chunks.values():
                chunk.vectors = {}
                chunk.metadata = {}
                chunk.size = 0
                chunk.active = True
                chunk.last_access = time.time()
            
            # 只保留第一个分块
            first_chunk_id = next(iter(self.chunks))
            self.chunks = {first_chunk_id: self.chunks[first_chunk_id]}
            self.current_chunk_id = first_chunk_id
            
            # 清空ID映射
            self.id_to_chunk = {}
            
            return count
    
    def save(self, path: str) -> bool:
        """保存向量存储到文件"""
        with self.lock:
            try:
                # 创建目录
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                
                # 保存元数据
                metadata = {
                    "dimension": self.dimension,
                    "chunk_size": self.chunk_size,
                    "max_active_chunks": self.max_active_chunks,
                    "parallelism": self.parallelism,
                    "id_to_chunk": self.id_to_chunk,
                    "current_chunk_id": self.current_chunk_id,
                    "chunks": list(self.chunks.keys())
                }
                
                with open(f"{path}.meta", "wb") as f:
                    pickle.dump(metadata, f)
                
                # 保存每个分块
                chunks_dir = f"{path}_chunks"
                os.makedirs(chunks_dir, exist_ok=True)
                
                for chunk_id, chunk in self.chunks.items():
                    chunk_path = os.path.join(chunks_dir, f"{chunk_id}.bin")
                    chunk.save(chunk_path)
                
                return True
            except Exception as e:
                logger.error(f"保存向量存储失败: {e}")
                return False
    
    def load(self, path: str) -> bool:
        """从文件加载向量存储"""
        with self.lock:
            try:
                # 加载元数据
                with open(f"{path}.meta", "rb") as f:
                    metadata = pickle.load(f)
                
                self.dimension = metadata["dimension"]
                self.chunk_size = metadata["chunk_size"]
                self.max_active_chunks = metadata["max_active_chunks"]
                self.parallelism = metadata["parallelism"]
                self.id_to_chunk = metadata["id_to_chunk"]
                self.current_chunk_id = metadata["current_chunk_id"]
                
                # 创建分块对象
                self.chunks = {}
                chunks_dir = f"{path}_chunks"
                
                for chunk_id in metadata["chunks"]:
                    self.chunks[chunk_id] = VectorChunk(id=chunk_id, dimension=self.dimension)
                
                # 只加载当前分块和最近使用的分块
                active_chunks = set([self.current_chunk_id])
                remaining_slots = self.max_active_chunks - 1
                
                # 为了效率，我们只加载有必要的分块
                # 剩余的分块会在需要时惰性加载
                if remaining_slots > 0:
                    # 找出被最多向量引用的分块
                    chunk_ref_count = {}
                    for chunk_id in self.id_to_chunk.values():
                        chunk_ref_count[chunk_id] = chunk_ref_count.get(chunk_id, 0) + 1
                    
                    # 按引用数排序并选择最常用的分块
                    sorted_chunks = sorted(chunk_ref_count.items(), key=lambda x: x[1], reverse=True)
                    for chunk_id, _ in sorted_chunks:
                        if chunk_id not in active_chunks and remaining_slots > 0:
                            active_chunks.add(chunk_id)
                            remaining_slots -= 1
                
                # 加载活跃分块
                for chunk_id in active_chunks:
                    chunk_path = os.path.join(chunks_dir, f"{chunk_id}.bin")
                    self.chunks[chunk_id].load(chunk_path)
                
                # 标记其他分块为非活跃
                for chunk_id in self.chunks:
                    if chunk_id not in active_chunks:
                        self.chunks[chunk_id].active = False
                
                self.initialized = True
                return True
            except Exception as e:
                logger.error(f"加载向量存储失败: {e}")
                self.initialized = False
                return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        with self.lock:
            stats = {
                "total_vectors": len(self.id_to_chunk),
                "dimension": self.dimension,
                "chunks": {
                    "total": len(self.chunks),
                    "active": sum(1 for c in self.chunks.values() if c.active),
                    "details": {}
                }
            }
            
            for chunk_id, chunk in self.chunks.items():
                stats["chunks"]["details"][chunk_id] = {
                    "size": chunk.size,
                    "active": chunk.active,
                    "last_access": chunk.last_access
                }
            
            return stats


def demo_sharded_vector_store():
    """演示分片向量存储功能"""
    print("\n=== 分片向量存储演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建分片向量存储
        print("创建分片向量存储...")
        vector_store = ShardedVectorStore(
            dimension=128,  # 使用较小的维度以加快演示速度
            chunk_size=100,  # 每个分片最多100个向量
            max_active_chunks=2,  # 同时最多2个活跃分片
            parallelism=2  # 2个并行线程
        )
        
        # 添加向量
        print(f"添加测试向量...")
        start_time = time.time()
        
        vectors_added = 0
        for i in range(100):  # 添加100个向量
            # 创建随机向量
            vector = np.random.normal(0, 1, 128).tolist()
            
            # 添加向量
            success = vector_store.add(
                id=f"item{i+1}",
                vector=vector,
                metadata={"text": f"这是第{i+1}个向量", "category": f"category{i%5}"}
            )
            
            if success:
                vectors_added += 1
        
        end_time = time.time()
        print(f"成功添加 {vectors_added} 个向量，耗时: {end_time - start_time:.2f}秒")
        
        # 获取存储统计信息
        stats = vector_store.get_stats()
        print(f"\n存储统计信息:")
        print(f"  总向量数: {stats['total_vectors']}")
        print(f"  分片数: {stats['chunks']['total']}")
        print(f"  活跃分片数: {stats['chunks']['active']}")
        
        # 执行搜索
        print("\n执行并行向量搜索...")
        query_vector = np.random.normal(0, 1, 128).tolist()
        
        start_time = time.time()
        results = vector_store.search(query_vector, limit=5)
        end_time = time.time()
        
        print(f"搜索耗时: {end_time - start_time:.4f}秒")
        print(f"找到 {len(results)} 个结果:")
        for id, score, metadata in results:
            print(f"  ID: {id}, 相似度分数: {score:.4f}, 类别: {metadata.get('category')}")
        
        # 保存和加载测试
        store_path = os.path.join(temp_dir, "sharded_vectors")
        print(f"\n保存向量存储到 {store_path}...")
        save_start = time.time()
        vector_store.save(store_path)
        save_end = time.time()
        print(f"保存耗时: {save_end - save_start:.2f}秒")
        
        # 创建新存储并加载
        print("加载向量存储...")
        new_store = ShardedVectorStore(dimension=128)
        load_start = time.time()
        new_store.load(store_path)
        load_end = time.time()
        print(f"加载耗时: {load_end - load_start:.2f}秒")
        
        # 验证加载的存储
        new_stats = new_store.get_stats()
        print(f"加载后的统计信息:")
        print(f"  总向量数: {new_stats['total_vectors']}")
        print(f"  分片数: {new_stats['chunks']['total']}")
        print(f"  活跃分片数: {new_stats['chunks']['active']}")


if __name__ == "__main__":
    demo_sharded_vector_store() 