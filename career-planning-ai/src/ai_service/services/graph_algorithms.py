import re
import math
import numpy as np
import igraph as ig
import leidenalg as la
from typing import Optional, Callable, Literal, Dict, List, Tuple
from collections import defaultdict
from ai_service.services import log
from sklearn.metrics.pairwise import cosine_similarity, manhattan_distances
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

__all__ = ["GraphAlgorithms"]


class GraphAlgorithms:

    # 安全获取无向边/双向边的值
    @staticmethod
    def _get_symmetric_value(edge_dict, node_a, node_b, default_val):
        """
        安全获取无向边/双向边的值，解决方向对称性陷阱
        """
        if (node_a, node_b) in edge_dict:
            return edge_dict[(node_a, node_b)]
        elif (node_b, node_a) in edge_dict:
            return edge_dict[(node_b, node_a)]
        return default_val

    # 通用Leiden聚类函数
    @staticmethod
    def run_clustering(
        edge_score_map: Dict[Tuple[str, str], float],
        nodes: Optional[List[str]] = None,
        resolution: float = 0.1,
        isolation_threshold: float = 0.1,
        weight_transform_fn: Callable[[float], float] = lambda x: x ** 2,
    ) -> Dict[str, int]:
        """
        通用的Leiden聚类函数
        input:
        - edge_score_map: dict[tuple[str, str], float]，无向边的权重映射
        - nodes: list[str]，所有节点的ID列表,必须包含edge_score_map中出现的所有节点,如果nodes中有edge_score_map没有的节点，则这些节点会被视为孤立点处理
        - resolution: float，Leiden聚类的分辨率参数，数值越小社区越少越粗，数值越大社区越多越细
        - isolation_threshold: float，孤立点比例阈值，超过则触发孤立点合并机制
        - weight_transform_fn: Callable[[float], float]，权重转换函数，默认是平方函数，可以根据需要调整以增强或平滑权重分布
        output:
        - community_map: dict[str, int]，节点ID到社区ID的映射
        """
        log.info("阶段1：第一次Leiden粗聚类（宏观划界）")

        if not nodes:
            nodes = list(set().union(*edge_score_map.keys())) if edge_score_map else []


        # 自动生成索引映射
        node_id_to_idx = {node_id: idx for idx, node_id in enumerate(nodes)}
        idx_to_node_id = {idx: node_id for node_id, idx in node_id_to_idx.items()}

        # 最终结果存储
        community_map = {}

        # 将边-权map拆成边列表和权重列表，方便igraph使用
        valid_edges = []
        valid_edge_weights = []

        processed_pairs = set()

        for (a, b), score in edge_score_map.items():
            if a not in node_id_to_idx or b not in node_id_to_idx:
                continue

            # 排序确保无向边唯一性
            pair = tuple(sorted((a, b)))
            if pair in processed_pairs:
                continue

            enhanced_weight = weight_transform_fn(score)
            valid_edges.append((node_id_to_idx[pair[0]], node_id_to_idx[pair[1]]))
            valid_edge_weights.append(enhanced_weight)
            processed_pairs.add(pair)

        log.info(f"基础网生成完成，有效边数：{len(valid_edges)}")

        # Leiden聚类
        log.info(f"Leiden聚类, resolution={resolution}")

        # 显式指定节点数，防止孤立节点索引错位
        graph = ig.Graph(n=len(nodes), edges=valid_edges, directed=False)
        part = la.find_partition(
            graph,
            la.RBConfigurationVertexPartition,
            weights=valid_edge_weights,
            resolution_parameter=resolution,
        )

        # 写入社区标签
        for idx, community_id in enumerate(part.membership):
            node_id = idx_to_node_id[idx]
            community_map[node_id] = community_id

        # 统计分析
        size_stats = defaultdict(int)
        for cid in part.membership:
            size_stats[cid] += 1

        # 孤立点处理(将其与最相似(即权重最高)的非孤立点合并)，解决孤立点过多导致社区碎片化问题
        isolated_indices = [idx for idx, cid in enumerate(part.membership) if size_stats[cid] == 1]
        isolation_ratio = list(size_stats.values()).count(1) / len(nodes)
        if isolation_ratio > isolation_threshold and len(isolated_indices) > 0:
            log.info(f"触发孤立点合并机制...")

            # 预计算：为了快速找到孤立点的最佳邻居，我们需要建立一个临时的邻接索引
            # 这样就不需要 O(N^2) 遍历，只需要查看该点已有的连接
            adj_scores = defaultdict(dict)
            for (a, b), score in edge_score_map.items():
                adj_scores[a][b] = score
                adj_scores[b][a] = score

            merged_count = 0
            for idx in isolated_indices:
                u_id = idx_to_node_id[idx]
                candidates = adj_scores.get(u_id, {})

                best_target_id = None
                max_w = -1.0

                # 在它的所有邻居中，找一个不属于孤立社区的
                for v_id, w in candidates.items():
                    v_idx = node_id_to_idx.get(v_id)
                    if v_idx is None:
                        continue

                    if size_stats[part.membership[v_idx]] > 1:  # 目标必须是非孤立社区
                        if w > max_w:
                            max_w = w
                            best_target_id = v_id

                if best_target_id:
                    old_cid = community_map[u_id]
                    target_cid = community_map[best_target_id]
                    community_map[u_id] = target_cid

                    # 更新统计数据
                    size_stats[target_cid] += 1
                    size_stats[old_cid] -= 1
                    if size_stats[old_cid] == 0:
                        del size_stats[old_cid]
                    merged_count += 1

            log.info(f"孤立点合并尝试完成，成功合并：{merged_count} 个，保持孤立：{len(isolated_indices) - merged_count} 个")

        log.info(
            f"Leiden聚类完成! | 社区总数：{len(size_stats)} "
            f"| 最大社区规模：{max(size_stats.values())} "
            f"| 孤立点(社区规模为1)数量：{list(size_stats.values()).count(1)}"
        )

        return community_map

    # 多目标计算 + 局部帕累托剪枝
    @staticmethod
    def run_pareto_sparsification(
            community_map: Dict[str, int],
            multi_objective_dict: Dict[str, Literal[0, 1]],
            edge_info_map: Dict[Tuple[str, str], dict],
            cross_community_penalty: float = 0.5,  # 跨社区转岗的基础难度惩罚，将作为最小化目标
            keep_fronts: int = 2  # 保留前几层帕累托前沿
    ) -> Dict[Tuple[str, str], dict]:
        """
        骨架提取，剔除同起点内的垃圾边
        input:
        - community_map: Dict[str, int]，节点ID到社区ID的映射
        - multi_objective_dict: Dict[str, Literal[0, 1]]，多目标定义, key是edge_info_map中每条边的指标名称，value是0或1，0表示该指标需要最小化，1表示该指标需要最大化
        - edge_info_map: Dict[Tuple[str, str], dict]，有向图的边信息映射

        """
        log.info("正在进行有向图中同社区内多目标计算 + 局部帕累托剪枝")

        # 最终结果存储
        pareto_skeleton_edges = {}
        nds = NonDominatedSorting()  # 实例化排序对象

        # 1. 动态拓展多目标字典（不污染原字典）
        local_mo_dict = multi_objective_dict.copy()
        TEMP_PENALTY_KEY = "_cross_community_penalty"
        local_mo_dict[TEMP_PENALTY_KEY] = 0  # 0 表示该新增指标需要最小化

        # 2. 预处理边：注入跨区标识与临时惩罚维度
        log.info("正在预处理候选边并动态注入跨区惩罚维度")
        processed_groups = defaultdict(list)

        for (f, t), m_info in edge_info_map.items():
            if f not in community_map or t not in community_map:
                continue

            metric = m_info.copy()  # 浅拷贝，保护原数据

            # 判定跨社区
            is_cross = community_map[f] != community_map[t]
            metric["is_cross_community"] = is_cross

            # 注入临时目标值
            metric[TEMP_PENALTY_KEY] = cross_community_penalty if is_cross else 0.0

            processed_groups[f].append((f, t, metric))

        if not processed_groups:
            log.warning("没有满足社区映射条件的有效边！")
            return {}

        # 3. 局部帕累托筛选
        log.info("正在按起点分组做局部非支配排序")
        obj_configs = list(local_mo_dict.items()) # 固定目标顺序

        for from_node, edges in processed_groups.items():
            # 孤边直接保留为第一前沿
            if len(edges) == 1:
                f, t, m = edges[0]
                m["pareto_rank"] = 0
                m["is_cross_community"] = m.get("is_cross_community", False) 
                m.pop(TEMP_PENALTY_KEY, None) # 清理临时键
                pareto_skeleton_edges[(f, t)] = m
                continue

            objs = []

            for f, t, m in edges:
                row =[]
                for obj_name, is_higher_better in obj_configs:
                    if obj_name not in m:
                        raise ValueError(f"指标 '{obj_name}' 缺失于边 ({f}, {t})")

                    val = m[obj_name]
                    # Pymoo 需要统一为最小化问题
                    row.append(-val if is_higher_better else val)
                objs.append(row)

            # 矩阵化并进行非支配排序
            objs = np.array(objs)
            fronts = nds.do(objs)

            # 4. 提取指定层数的前沿解
            for rank in range(min(len(fronts), keep_fronts)):
                for idx in fronts[rank]:
                    f, t, m = edges[idx]

                    # 记录是第几层前沿
                    m["pareto_rank"] = rank

                    # 清理内部使用的临时属性，保持输出结构干净
                    m.pop(TEMP_PENALTY_KEY, None)

                    pareto_skeleton_edges[(f, t)] = m

        log.info(f"帕累托剪枝完成！保留前沿边数：{len(pareto_skeleton_edges)}")
        return pareto_skeleton_edges

    # 计算加权杰卡德相似度
    @staticmethod
    def calculate_weighted_jaccard(data: List[dict], threshold: float = 0.1) -> Dict[Tuple[str, str], float]:
        # 构建内存结构：job_id → {comp_name: weight}
        job_comp_weights = defaultdict(dict)
        all_job_ids = set()
        for item in data:
            j_id = item["job_id"]
            c_name = item["comp_name"]
            weight = item["weight"]
            job_comp_weights[j_id][c_name] = weight
            all_job_ids.add(j_id)

        all_jobs = list(all_job_ids)

        # --- 提纯版：极致优化的加权 Jaccard 计算 ---
        log.info("开始计算加权杰卡德相似度 (Min/Max 算法)...")
        jaccard_map = {}

        # 【优化 1】预先计算每个岗位的所有技能权重之和 (空间换时间)
        job_sum_weights = {job: sum(comps.values()) for job, comps in job_comp_weights.items()}

        # 记录有效边数
        valid_edges = 0

        for i in range(len(all_jobs)):
            job_a = all_jobs[i]
            comps_a = job_comp_weights[job_a]
            sum_a = job_sum_weights[job_a]

            # 性能追踪打印
            if i % 1000 == 0 and i > 0:
                log.info(f"  已处理 {i}/{len(all_jobs)} 个岗位，当前有效边数：{valid_edges}...")

            for j in range(i + 1, len(all_jobs)):
                job_b = all_jobs[j]
                comps_b = job_comp_weights[job_b]
                sum_b = job_sum_weights[job_b]

                sum_intersect = 0.0

                # 【优化 3】只遍历较小的字典，寻找交集 (极大减少循环次数)
                smaller_comps, larger_comps = (comps_a, comps_b) if len(comps_a) < len(comps_b) else (comps_b, comps_a)

                # 计算标准的 Min 交集
                for c, weight_small in smaller_comps.items():
                    if c in larger_comps:
                        sum_intersect += min(weight_small, larger_comps[c])

                # 快速过滤：如果毫无交集，直接跳过
                if sum_intersect == 0:
                    continue

                # 【优化 4】利用数学恒等式瞬间算出并集 Max 之和：
                # Sum(Max) = Sum(A) + Sum(B) - Sum(Min)
                sum_union = sum_a + sum_b - sum_intersect

                score = round(sum_intersect / sum_union, 4)

                # 【优化 5】内存保护：只保留有演化价值的边
                if score > threshold:
                    jaccard_map[(job_a, job_b)] = score
                    valid_edges += 1

        if valid_edges == 0:
            raise ValueError("硬筛选后无有效边，请调低Jaccard阈值")
        log.info(f"基础网生成完成，有效边数：{valid_edges}")

        return jaccard_map  

    # 计算 IDF 权重列表
    @staticmethod
    def get_idf_weights(raw_data: List[dict], threshold: float = 0.1) -> Optional[List[dict]]:
        if not raw_data:
            return None

        # 2. 在纯内存中进行极速代数统计 (告别 Pydantic)
        total_jobs = len(set(row['job_id'] for row in raw_data))
        if total_jobs == 0:
            log.warning("无有效岗位数据, 跳过IDF计算")
            return None
        comp_df = defaultdict(int)  # 记录每个能力在多少个岗位中出现过

        for row in raw_data:
            comp_df[row['comp_name']] += 1

        # 3. 计算 IDF 权重列表
        # 使用平滑对数公式防止除零，基数为 e
        idf_updates =[]
        for comp_name, df in comp_df.items():
            # 经典 IDF 公式：log( N / DF )
            # 加上 1.0 是为了防止过于普遍的技能权重变成 0
            if not raw_data:
                return None
            idf_value = math.log(total_jobs / df) + 1.0 

            idf_updates.append({
                "comp_name": comp_name,
                "idf_weight": round(idf_value, 4)
            })

        log.info(f"Calculated IDF for {len(idf_updates)} unique competencies.")

        return idf_updates
