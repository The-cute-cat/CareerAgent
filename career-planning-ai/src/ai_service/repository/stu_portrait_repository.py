from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from ai_service.models.stu_profile import StuProfile  # 导入 StuProfile 类


class StuProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ================= Create =================

    async def create(self, profile: StuProfile) -> StuProfile:
        """
        创建单个学生画像
        Args:
            profile: StuProfile 模型实例
        Returns:
            StuProfile: 创建后的对象（包含生成的 ID 和时间戳）
        """
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)  # 刷新以获取数据库生成的 ID 和时间戳
        return profile

    async def create_all(self, profile_list: List[StuProfile]) -> List[StuProfile]:
        """
        批量创建学生画像
        Args:
            profile_list: StuProfile 模型实例列表
        Returns:
            List[StuProfile]: 创建后的对象列表
        """
        self.session.add_all(profile_list)
        await self.session.commit()
        # 刷新所有对象以获取生成的 ID 和时间戳
        for profile in profile_list:
            await self.session.refresh(profile)
        return profile_list

    # ================= Read =================

    async def get_by_id(self, profile_id: int) -> Optional[StuProfile]:
        """
        根据主键 ID 获取学生画像
        """
        stmt = select(StuProfile).where(StuProfile.id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stu_id(self, stu_id: int) -> Optional[StuProfile]:
        """
        根据学生 ID (stu_id) 获取学生画像
        这是最常用的查询方式，因为通常是一对一关系
        """
        stmt = select(StuProfile).where(StuProfile.stu_id == stu_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(
            self,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取学生画像列表 (支持分页和简单过滤)
        返回：{ "total": int, "items": List[StuProfile], "page": int, "page_size": int }
        """
        # 1. 构建查询语句
        stmt = select(StuProfile)

        # 2. 动态添加过滤条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(StuProfile, key) and value is not None:
                    # 特殊处理：如果是 stu_id 精确匹配，其他字符串模糊匹配
                    if key == "stu_id":
                        conditions.append(getattr(StuProfile, key) == value)
                    elif isinstance(value, str):
                        conditions.append(getattr(StuProfile, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(StuProfile, key) == value)
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
    ) -> List[StuProfile]:
        """
        获取学生画像列表 (支持过滤，返回全部结果，不分页)
        """
        stmt = select(StuProfile)

        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(StuProfile, key) and value is not None:
                    if key == "stu_id":
                        conditions.append(getattr(StuProfile, key) == value)
                    elif isinstance(value, str):
                        conditions.append(getattr(StuProfile, key).like(f"%{value}%"))
                    else:
                        conditions.append(getattr(StuProfile, key) == value)
            if conditions:
                stmt = stmt.where(*conditions)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ================= Update =================

    async def update(self, profile_id: int, update_data: Dict[str, Any]) -> Optional[StuProfile]:
        """
        根据主键 ID 更新学生画像信息
        """
        profile = await self.get_by_id(profile_id)
        if not profile:
            return None

        # 遍历更新数据
        for key, value in update_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update_by_stu_id(self, stu_id: int, update_data: Dict[str, Any]) -> Optional[StuProfile]:
        """
        根据学生 ID (stu_id) 更新或创建学生画像
        如果不存在则创建，存在则更新 (Upsert 逻辑简化版)
        """
        profile = await self.get_by_stu_id(stu_id)

        if not profile:
            # 如果不存在，创建新的
            new_profile = StuProfile(stu_id=stu_id, **update_data)
            return await self.create(new_profile)
        else:
            # 如果存在，更新现有
            for key, value in update_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            await self.session.commit()
            await self.session.refresh(profile)
            return profile

    # ================= Delete =================

    async def delete(self, profile_id: int) -> bool:
        """
        根据主键 ID 删除学生画像
        """
        profile = await self.get_by_id(profile_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.commit()
        return True

    async def delete_by_stu_id(self, stu_id: int) -> bool:
        """
        根据学生 ID (stu_id) 删除学生画像
        """
        profile = await self.get_by_stu_id(stu_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.commit()
        return True