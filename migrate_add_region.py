from sqlalchemy import create_engine, text

# Adjust this if you renamed your SQLite file
engine = create_engine("sqlite:///memory.db")

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE user_profiles ADD COLUMN region TEXT"))
        print("✅ Column 'region' added to user_profiles.")
    except Exception as e:
        print(f"⚠️ Could not alter table: {e}")
