# jobinfo的一些CRUD操作
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from ai_service.models.job_info import JobInfo  # 导入你提供的 JobInfo 类


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_all(self, job_list: List[JobInfo])->List[JobInfo]:
        """
                批量创建岗位

                Args:
                    job_list: JobInfo 模型实例列表

                Returns:
                    List[JobInfo]: 创建后的岗位对象列表（包含生成的 ID 和时间戳）
        """
        self.session.add_all(job_list)
        await self.session.commit()
        # 3. 刷新所有对象以获取生成的 ID 和时间戳
        for job in job_list:
            await self.session.refresh(job)
        return job_list

    async def create(self,job:JobInfo) -> JobInfo:
        """
                    创建单个岗位
                    Args:
                        job: JobInfo 模型实例

                    Returns:
                        JobInfo: 创建后的岗位对象（包含生成的 ID 和时间戳）
        """
        # job = JobInfo(**job_data)

        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)  # 刷新以获取数据库生成的 ID 和时间戳
        return job

    async def get_by_id(self, job_id: int) -> Optional[JobInfo]:
        """
        根据 ID 获取岗位
        """
        stmt = select(JobInfo).where(JobInfo.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_all(
            self,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[JobInfo]:
        """
        获取岗位列表 (支持过滤，返回全部结果)

        Args:
            filters: 过滤条件字典，如 {"job_title": "Python", "location": "北京"}

        Returns:
            List[JobInfo]: 所有符合条件的岗位对象列表
        """
        # 1. 构建查询语句
        stmt = select(JobInfo)

        # 2. 动态添加过滤条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(JobInfo, key) and value is not None:
                    # 字符串使用模糊匹配，其他类型使用精确匹配
                    if isinstance(value, str):
                        conditions.append(getattr(JobInfo, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(JobInfo, key) == value)
            if conditions:
                stmt = stmt.where(*conditions)

        # 3. 执行查询 (无分页限制)
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        # 4. 直接返回列表
        return items

    async def get_list(
            self,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取岗位列表 (支持分页和简单过滤)
        返回：{ "total": int, "items": List[JobInfo] }
        """
        # 1. 构建查询语句
        stmt = select(JobInfo)

        # 2. 动态添加过滤条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(JobInfo, key) and value is not None:
                    # 简单模糊匹配示例，可根据需求调整
                    if isinstance(value, str):
                        conditions.append(getattr(JobInfo, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(JobInfo, key) == value)
            if conditions:
                stmt = stmt.where(*conditions)

        # 3. 获取总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one() or 0

        # 4. 分页
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # 5. 执行查询
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    async def update(self, job_id: int, update_data: Dict[str, Any]) -> Optional[JobInfo]:
        """
        更新岗位信息
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None

        # 遍历更新数据
        for key, value in update_data.items():
            if hasattr(job, key):
                setattr(job, key, value)

        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def delete(self, job_id: int) -> bool:
        """
        删除岗位
        """
        job = await self.get_by_id(job_id)
        if not job:
            return False

        await self.session.delete(job)
        await self.session.commit()
        return True