from . import BaseModel, db
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any
from datetime import datetime, timedelta


class TimeBlockTemplate(BaseModel):
    """时间块模板模型"""
    __tablename__ = 'time_block_templates'

    name = db.Column(String(100), nullable=False)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    description = db.Column(Text)
    is_default = db.Column(Boolean, default=False)

    # 关联关系
    user = relationship('User', back_populates='time_block_templates')
    time_blocks = relationship('TimeBlock', back_populates='template')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'user_id': self.user_id,
            'description': self.description,
            'is_default': self.is_default,
            'time_block_count': self.get_time_block_count()
        })
        return base_dict

    def get_time_block_count(self) -> int:
        """获取模板关联的时间块数量"""
        return len(self.time_blocks) if self.time_blocks else 0

    def apply_to_date(self, target_date: datetime) -> list:
        """将模板应用到指定日期，生成时间块列表"""
        time_blocks = []

        # 这里应该根据模板配置生成时间块
        # 由于模板的具体配置逻辑比较复杂，这里提供一个基础实现
        # 实际实现应该根据模板的具体配置（如时间段、类型等）生成时间块

        # 示例：生成一个基础的工作日模板
        if self.name == "标准工作日":
            time_blocks = self._generate_standard_workday(target_date)
        elif self.name == "深度工作模式":
            time_blocks = self._generate_deep_work_day(target_date)
        else:
            # 默认实现：复制模板中已有的时间块配置
            time_blocks = self._copy_existing_time_blocks(target_date)

        return time_blocks

    def _generate_standard_workday(self, target_date: datetime) -> list:
        """生成标准工作日时间块"""
        from models.time_block import TimeBlock, BlockType

        time_blocks = []
        base_time = datetime.combine(target_date, datetime.min.time())

        # 上午工作时间（9:00-12:00）
        time_blocks.append(TimeBlock(
            user_id=self.user_id,
            date=target_date,
            start_time=base_time.replace(hour=9, minute=0),
            end_time=base_time.replace(hour=12, minute=0),
            block_type=BlockType.RESEARCH,
            color='#FF5733',
            template_id=self.id
        ))

        # 下午工作时间（13:00-17:00）
        time_blocks.append(TimeBlock(
            user_id=self.user_id,
            date=target_date,
            start_time=base_time.replace(hour=13, minute=0),
            end_time=base_time.replace(hour=17, minute=0),
            block_type=BlockType.GROWTH,
            color='#33FF57',
            template_id=self.id
        ))

        return time_blocks

    def _generate_deep_work_day(self, target_date: datetime) -> list:
        """生成深度工作模式时间块"""
        from models.time_block import TimeBlock, BlockType

        time_blocks = []
        base_time = datetime.combine(target_date, datetime.min.time())

        # 深度工作块（9:00-12:00）
        time_blocks.append(TimeBlock(
            user_id=self.user_id,
            date=target_date,
            start_time=base_time.replace(hour=9, minute=0),
            end_time=base_time.replace(hour=12, minute=0),
            block_type=BlockType.RESEARCH,
            color='#FF5733',
            template_id=self.id
        ))

        # 学习块（14:00-16:00）
        time_blocks.append(TimeBlock(
            user_id=self.user_id,
            date=target_date,
            start_time=base_time.replace(hour=14, minute=0),
            end_time=base_time.replace(hour=16, minute=0),
            block_type=BlockType.GROWTH,
            color='#33FF57',
            template_id=self.id
        ))

        # 复盘块（16:30-17:00）
        time_blocks.append(TimeBlock(
            user_id=self.user_id,
            date=target_date,
            start_time=base_time.replace(hour=16, minute=30),
            end_time=base_time.replace(hour=17, minute=0),
            block_type=BlockType.REVIEW,
            color='#3357FF',
            template_id=self.id
        ))

        return time_blocks

    def _copy_existing_time_blocks(self, target_date: datetime) -> list:
        """复制模板中已有的时间块配置"""
        from models.time_block import TimeBlock

        time_blocks = []

        for existing_block in self.time_blocks:
            # 创建新的时间块，保持相对时间关系
            new_start = datetime.combine(target_date, existing_block.start_time.time())
            new_end = datetime.combine(target_date, existing_block.end_time.time())

            time_blocks.append(TimeBlock(
                user_id=self.user_id,
                date=target_date,
                start_time=new_start,
                end_time=new_end,
                block_type=existing_block.block_type,
                color=existing_block.color,
                template_id=self.id
            ))

        return time_blocks

    def clone(self) -> 'TimeBlockTemplate':
        """克隆模板"""
        new_template = TimeBlockTemplate(
            name=f"{self.name} (副本)",
            user_id=self.user_id,
            description=self.description,
            is_default=False  # 副本不能是默认模板
        )
        return new_template