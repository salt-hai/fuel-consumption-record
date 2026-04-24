"""
迁移脚本：给 vehicles 表添加 user_id 外键

运行方式：
    python add_user_id_to_vehicles.py
"""
import asyncio
import sqlite3
from pathlib import Path
from sqlalchemy import text
from database import engine, Base, async_sessionmaker
from models.user import User
from models.vehicle import Vehicle

async def migrate():
    """执行迁移"""

    # 1. 获取数据库路径（可能在 data 目录或 server 目录）
    db_path_data = Path(__file__).parent.parent / "data" / "fuel.db"
    db_path_server = Path(__file__).parent / "fuel.db"

    # 使用存在的数据库路径
    if db_path_data.exists():
        db_path = db_path_data
    elif db_path_server.exists():
        db_path = db_path_server
    else:
        # 默认使用 server 目录
        db_path = db_path_server

    # 确保 data 目录存在
    if db_path.parent != Path(__file__).parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Database path: {db_path}")

    # 检查数据库文件是否存在
    if not db_path.exists():
        print(f"Warning: Database file not exists {db_path}")
        print("Please start backend service first to create database")
        return

    # 2. 使用 sqlite3 直接操作（添加列）
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 检查 user_id 列是否已存在
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'user_id' in columns:
            print("[OK] user_id column already exists, skipping")
        else:
            # 添加 user_id 列
            cursor.execute("ALTER TABLE vehicles ADD COLUMN user_id INTEGER")
            print("[OK] Added user_id column")

        # 检查是否有现有数据需要设置默认值
        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE user_id IS NULL")
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            # 获取第一个用户 ID
            cursor.execute("SELECT id FROM users LIMIT 1")
            user_row = cursor.fetchone()

            if user_row:
                first_user_id = user_row[0]
                cursor.execute(f"UPDATE vehicles SET user_id = {first_user_id} WHERE user_id IS NULL")
                print(f"[OK] Set default user for {null_count} records (user_id={first_user_id})")
            else:
                print("[WARN] No users in database, please register first")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

    print("\nMigration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
