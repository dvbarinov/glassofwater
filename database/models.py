from sqlalchemy import MetaData, Table, Column, Integer, BigInteger, DateTime, String, Boolean

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("gender", Integer),  # 0 = male, 1 = female, NULL = not set
    Column("weight_kg", Integer),
    Column("activity_level", Integer),  # 0, 1, 2
    Column("daily_goal_ml", Integer, default=2000),
    Column("timezone_offset", Integer, default=0),  # в минутах от UTC
    Column("unit_preference", String(10), default="ml"),  # "ml" or "cups"
    Column("notifications_enabled", Boolean, default=True),
)

intakes = Table(
    "intakes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", BigInteger),
    Column("amount_ml", Integer),
    Column("timestamp", DateTime),
)