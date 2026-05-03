"""后台首页统计服务。"""

from datetime import datetime, timedelta

from sqlalchemy import func

from app.models import KbDocument, KnowledgeBase, QaMessage, SysUser


class DashboardService:
    """聚合管理后台首页所需的统计指标与图表数据。"""

    @staticmethod
    def get_dashboard_data():
        """返回统计卡片与图表数据。"""

        today_start = datetime.combine(datetime.now().date(), datetime.min.time())
        seven_days_ago = today_start - timedelta(days=6)

        summary = {
            "userCount": SysUser.query.count(),
            "knowledgeBaseCount": KnowledgeBase.query.count(),
            "documentCount": KbDocument.query.count(),
            "todayQaCount": QaMessage.query.filter(QaMessage.created_at >= today_start).count(),
        }

        trend_rows = (
            QaMessage.query.with_entities(
                func.date(QaMessage.created_at).label("day"),
                func.count(QaMessage.id).label("count"),
            )
            .filter(QaMessage.created_at >= seven_days_ago)
            .group_by(func.date(QaMessage.created_at))
            .order_by(func.date(QaMessage.created_at))
            .all()
        )
        trend_map = {str(row.day): row.count for row in trend_rows}

        trend = []
        for offset in range(7):
            current_day = (seven_days_ago + timedelta(days=offset)).date()
            trend.append(
                {
                    "date": current_day.strftime("%m-%d"),
                    "count": trend_map.get(str(current_day), 0),
                }
            )

        distribution_rows = (
            KnowledgeBase.query.with_entities(
                KnowledgeBase.name,
                func.count(KbDocument.id).label("count"),
            )
            .outerjoin(KbDocument, KnowledgeBase.id == KbDocument.knowledge_base_id)
            .group_by(KnowledgeBase.id, KnowledgeBase.name)
            .order_by(KnowledgeBase.id.asc())
            .all()
        )
        distribution = [{"name": row.name, "count": row.count} for row in distribution_rows]

        return {"summary": summary, "qaTrend": trend, "documentDistribution": distribution}
