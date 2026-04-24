"""
迁移脚本：给 vehicles 表添加 user_id 外键

运行方式：
    python add_user_id_to_vehicles.py
"""
import sqlite3
from pathlib import Path

def migrate():
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
            print("[OK] user_id column already exists")

            # 检查是否已有 NOT NULL 约束
            cursor.execute("PRAGMA table_info(vehicles)")
            columns_info = cursor.fetchall()
            user_id_notnull = None
            for col in columns_info:
                if col[1] == 'user_id':
                    user_id_notnull = col[3]
                    break

            if user_id_notnull == 1:
                print("[OK] user_id column already has NOT NULL constraint")
            else:
                # SQLite 不支持直接修改列约束，需要重建表
                print("[INFO] Adding NOT NULL constraint to user_id column...")

                # 1. 创建新表
                cursor.execute("""
                    CREATE TABLE vehicles_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name VARCHAR NOT NULL,
                        icon VARCHAR DEFAULT '🚗',
                        brand VARCHAR,
                        model VARCHAR,
                        plate_number VARCHAR UNIQUE,
                        initial_odometer INTEGER DEFAULT 0,
                        fuel_type VARCHAR DEFAULT '92号汽油',
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 2. 复制数据
                cursor.execute("""
                    INSERT INTO vehicles_new (id, user_id, name, icon, brand, model, plate_number, initial_odometer, fuel_type, is_active, created_at)
                    SELECT id, user_id, name, icon, brand, model, plate_number, initial_odometer, fuel_type, is_active, created_at
                    FROM vehicles
                """)

                # 3. 删除旧表
                cursor.execute("DROP TABLE vehicles")

                # 4. 重命名新表
                cursor.execute("ALTER TABLE vehicles_new RENAME TO vehicles")

                # 5. 重建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_vehicles_user_id ON vehicles(user_id)")

                print("[OK] NOT NULL constraint added successfully")
        else:
            # 添加 user_id 列（先允许 NULL，然后设置默认值，最后重建表添加约束）
            cursor.execute("ALTER TABLE vehicles ADD COLUMN user_id INTEGER")
            print("[OK] Added user_id column")

            # 为现有数据设置默认值
            cursor.execute("SELECT COUNT(*) FROM vehicles WHERE user_id IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count > 0:
                cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
                user_row = cursor.fetchone()

                if user_row:
                    first_user_id = user_row[0]
                    cursor.execute(f"UPDATE vehicles SET user_id = {first_user_id} WHERE user_id IS NULL")
                    print(f"[OK] Set default user for {null_count} records (user_id={first_user_id})")
                else:
                    print("[WARN] No users in database, please register first")

            # 重建表添加 NOT NULL 约束
            print("[INFO] Adding NOT NULL constraint to user_id column...")
            cursor.execute("""
                CREATE TABLE vehicles_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    icon VARCHAR DEFAULT '🚗',
                    brand VARCHAR,
                    model VARCHAR,
                    plate_number VARCHAR UNIQUE,
                    initial_odometer INTEGER DEFAULT 0,
                    fuel_type VARCHAR DEFAULT '92号汽油',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                INSERT INTO vehicles_new (id, user_id, name, icon, brand, model, plate_number, initial_odometer, fuel_type, is_active, created_at)
                SELECT id, user_id, name, icon, brand, model, plate_number, initial_odometer, fuel_type, is_active, created_at
                FROM vehicles
            """)

            cursor.execute("DROP TABLE vehicles")
            cursor.execute("ALTER TABLE vehicles_new RENAME TO vehicles")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_vehicles_user_id ON vehicles(user_id)")

            print("[OK] NOT NULL constraint added successfully")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

    print("\nMigration completed!")

if __name__ == "__main__":
    migrate()
