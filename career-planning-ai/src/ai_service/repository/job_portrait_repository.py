from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from ai_service.models.job_portrait import JobPortrait  # 导入刚才创建的 JobPortrait 类


class JobPortraitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ================= Create =================

    async def create(self, portrait: JobPortrait) -> JobPortrait:
        """
        创建单个岗位画像
        Args:
            portrait: JobPortrait 模型实例
        Returns:
            JobPortrait: 创建后的对象（包含生成的 ID 和时间戳）
        """
        self.session.add(portrait)
        await self.session.commit()
        await self.session.refresh(portrait)  # 刷新以获取数据库生成的 ID 和时间戳
        return portrait

    async def create_all(self, portrait_list: List[JobPortrait]) -> List[JobPortrait]:
        """
        批量创建岗位画像
        Args:
            portrait_list: JobPortrait 模型实例列表
        Returns:
            List[JobPortrait]: 创建后的对象列表
        """
        self.session.add_all(portrait_list)
        await self.session.commit()
        # 刷新所有对象以获取生成的 ID 和时间戳
        for portrait in portrait_list:
            await self.session.refresh(portrait)
        return portrait_list

    # ================= Read =================

    async def get_by_id(self, portrait_id: int) -> Optional[JobPortrait]:
        """
        根据主键 ID 获取岗位画像
        """
        stmt = select(JobPortrait).where(JobPortrait.id == portrait_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_job_id(self, job_id: int) -> Optional[JobPortrait]:
        """
        根据岗位 ID (job_id) 获取岗位画像
        这是最常用的查询方式，因为通常是一对一关系
        """
        stmt = select(JobPortrait).where(JobPortrait.job_id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(
            self,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取岗位画像列表 (支持分页和简单过滤)
        返回：{ "total": int, "items": List[JobPortrait], "page": int, "page_size": int }
        """
        # 1. 构建查询语句
        stmt = select(JobPortrait)

        # 2. 动态添加过滤条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(JobPortrait, key) and value is not None:
                    # 特殊处理：如果是 job_id 精确匹配，其他字符串模糊匹配
                    if key == "job_id":
                        conditions.append(getattr(JobPortrait, key) == value)
                    elif isinstance(value, str):
                        conditions.append(getattr(JobPortrait, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(JobPortrait, key) == value)
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

    async def get_list_all(
            self,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[JobPortrait]:
        """
        获取岗位画像列表 (支持过滤，返回全部结果，不分页)
        """
        stmt = select(JobPortrait)

        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(JobPortrait, key) and value is not None:
                    if key == "job_id":
                        conditions.append(getattr(JobPortrait, key) == value)
                    elif isinstance(value, str):
                        conditions.append(getattr(JobPortrait, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(JobPortrait, key) == value)
            if conditions:
                stmt = stmt.where(*conditions)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ================= Update =================

    async def update(self, portrait_id: int, update_data: Dict[str, Any]) -> Optional[JobPortrait]:
        """
        根据主键 ID 更新岗位画像信息
        """
        portrait = await self.get_by_id(portrait_id)
        if not portrait:
            return None

        # 遍历更新数据
        for key, value in update_data.items():
            if hasattr(portrait, key):
                setattr(portrait, key, value)

        await self.session.commit()
        await self.session.refresh(portrait)
        return portrait

    async def update_by_job_id(self, job_id: int, update_data: Dict[str, Any]) -> Optional[JobPortrait]:
        """
        根据岗位 ID (job_id) 更新或创建岗位画像
        如果不存在则创建，存在则更新 (Upsert 逻辑简化版)
        """
        portrait = await self.get_by_job_id(job_id)

        if not portrait:
            # 如果不存在，创建新的
            new_portrait = JobPortrait(job_id=job_id, **update_data)
            return await self.create(new_portrait)
        else:
            # 如果存在，更新现有
            for key, value in update_data.items():
                if hasattr(portrait, key):
                    setattr(portrait, key, value)

            await self.session.commit()
            await self.session.refresh(portrait)
            return portrait

    # ================= Delete =================

    async def delete(self, portrait_id: int) -> bool:
        """
        根据主键 ID 删除岗位画像
        """
        portrait = await self.get_by_id(portrait_id)
        if not portrait:
            return False

        await self.session.delete(portrait)
        await self.session.commit()
        return True

    async def delete_by_job_id(self, job_id: int) -> bool:
        """
        根据岗位 ID (job_id) 删除岗位画像
        """
        portrait = await self.get_by_job_id(job_id)
        if not portrait:
            return False

        await self.session.delete(portrait)
        await self.session.commit()
        return True