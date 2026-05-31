"""
ETL Job - Runs nightly via GitHub Actions
Demonstrates: GitHub Actions → Supabase connection
"""

import os
import json
import psycopg2
from datetime import datetime

def log_job(conn, job_name: str, status: str, records: int = 0, error: str = None):
    """Log ETL job execution to database"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.etl_logs (job_name, status, started_at, completed_at, records_processed, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (job_name, status, datetime.utcnow(), datetime.utcnow(), records, error))
    conn.commit()
    cursor.close()

def run_etl():
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set")
        return False
    
    print(f"[{datetime.utcnow().isoformat()}] Starting ETL job...")
    
    try:
        conn = psycopg2.connect(db_url)
        print("✓ Connected to Supabase Postgres")
        
        # Demo: Update customer statistics
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE public.customers c
            SET 
                total_orders = (SELECT COUNT(*) FROM public.orders o WHERE o.customer_id = c.id),
                total_revenue = (SELECT COALESCE(SUM(total_amount), 0) FROM public.orders o WHERE o.customer_id = c.id),
                updated_at = NOW()
        """)
        rows_updated = cursor.rowcount
        conn.commit()
        cursor.close()
        
        print(f"✓ Updated {rows_updated} customer records")
        
        # Log success
        log_job(conn, "nightly_customer_stats", "success", rows_updated)
        
        conn.close()
        print(f"[{datetime.utcnow().isoformat()}] ETL job completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ ETL job failed: {str(e)}")
        try:
            conn = psycopg2.connect(db_url)
            log_job(conn, "nightly_customer_stats", "failed", 0, str(e))
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    success = run_etl()
    exit(0 if success else 1)
