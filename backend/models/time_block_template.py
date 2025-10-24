from . import BaseModel, db
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any, List
from datetime import datetime, timedelta


class TimeBlockTemplate(BaseModel):
    """时间块模板模型"""
    __tablename__ = 'time_block_templates'

    name = db.Column(String(100), nullable=False)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    description = db.Column(Text)
    is_default = db.Column(Boolean, default=False)

    # 模板类型
    template_type = db.Column(String(50), default='custom')  # 'preset', 'custom'

    # 关联关系
    user = relationship('User', back_populates='time_block_templates')
    time_blocks = relationship('TimeBlock', back_populates='template')
    configurations = relationship('TimeBlockTemplateConfig', back_populates='template', lazy='dynamic')

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

        try:
            # 优先使用配置表生成时间块
            if self.template_type == 'custom':
                configs = self.configurations.filter_by(is_active=True).order_by('order_index').all()
                if configs:
                    time_blocks = self._generate_from_configs(target_date, configs)
                else:
                    # 如果没有配置，使用预设模板
                    time_blocks = self._generate_preset_template(target_date)
            else:
                # 预设模板
                time_blocks = self._generate_preset_template(target_date)

        except Exception as e:
            # 出错时使用回退逻辑
            time_blocks = self._copy_existing_time_blocks(target_date)

        return time_blocks

    def _generate_from_configs(self, target_date: datetime, configs: List) -> list:
        """基于配置生成时间块"""
        from .time_block import TimeBlock, BlockType

        time_blocks = []
        base_date = datetime.combine(target_date, datetime.min.time())

        for config in configs:
            try:
                # 解析时间
                start_time = datetime.strptime(config.start_time, '%H:%M').time()
                end_time = datetime.strptime(config.end_time, '%H:%M').time()

                # 创建时间块
                start_datetime = datetime.combine(target_date, start_time)
                end_datetime = datetime.combine(target_date, end_time)

                # 处理跨日期情况
                if end_datetime < start_datetime:
                    end_datetime = datetime.combine(target_date + timedelta(days=1), end_time)

                time_block = TimeBlock(
                    user_id=self.user_id,
                    date=target_date,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    block_type=getattr(BlockType, config.block_type, BlockType.GROWTH),
                    color=config.color,
                    template_id=self.id
                )
                time_blocks.append(time_block)

            except (ValueError, AttributeError) as e:
                # 跳过无效配置，继续处理其他配置
                continue

        return time_blocks

    def _generate_preset_template(self, target_date: datetime) -> list:
        """生成预设模板"""
        if self.name == "标准工作日":
            return self._generate_standard_workday(target_date)
        elif self.name == "深度工作模式":
            return self._generate_deep_work_day(target_date)
        else:
            return self._copy_existing_time_blocks(target_date)

    def _generate_standard_workday(self, target_date: datetime) -> list:
        """生成标准工作日时间块"""
        from .time_block import TimeBlock, BlockType

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
        from .time_block import TimeBlock, BlockType

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
        from .time_block import TimeBlock

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