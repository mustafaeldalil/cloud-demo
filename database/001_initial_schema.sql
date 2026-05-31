-- Cloud Demo Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Chat logs table (for testing AI integration)
CREATE TABLE IF NOT EXISTS public.chat_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample customers table (for testing queries)
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    total_orders INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample orders table
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    customer_id UUID REFERENCES public.customers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ETL job logs (for GitHub Actions tracking)
CREATE TABLE IF NOT EXISTS public.etl_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- Row Level Security
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.etl_logs ENABLE ROW LEVEL SECURITY;

-- Policies for chat_logs (users can only see their own logs)
CREATE POLICY "Users can view own chat logs" ON public.chat_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat logs" ON public.chat_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policies for customers (authenticated users can read)
CREATE POLICY "Authenticated users can view customers" ON public.customers
    FOR SELECT TO authenticated USING (true);

-- Policies for orders (authenticated users can read)
CREATE POLICY "Authenticated users can view orders" ON public.orders
    FOR SELECT TO authenticated USING (true);

-- Policies for etl_logs (authenticated users can read)
CREATE POLICY "Authenticated users can view etl logs" ON public.etl_logs
    FOR SELECT TO authenticated USING (true);

-- Service role can do everything (for backend)
CREATE POLICY "Service role full access chat_logs" ON public.chat_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access customers" ON public.customers
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access orders" ON public.orders
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access etl_logs" ON public.etl_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Insert sample data
INSERT INTO public.customers (name, email, company, total_orders, total_revenue) VALUES
    ('Ahmed Hassan', 'ahmed@example.com', 'Tech Solutions', 15, 45000.00),
    ('Sara Mohamed', 'sara@example.com', 'Digital Agency', 8, 22500.00),
    ('Omar Ali', 'omar@example.com', 'Startup Inc', 23, 67800.00),
    ('Fatima Khalil', 'fatima@example.com', 'Enterprise Corp', 42, 125000.00),
    ('Youssef Ibrahim', 'youssef@example.com', 'SMB Ltd', 5, 8500.00)
ON CONFLICT (email) DO NOTHING;

-- Insert sample orders
INSERT INTO public.orders (customer_id, order_number, status, total_amount)
SELECT 
    c.id,
    'ORD-' || LPAD(ROW_NUMBER() OVER ()::TEXT, 6, '0'),
    CASE (RANDOM() * 3)::INT 
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'processing'
        WHEN 2 THEN 'completed'
        ELSE 'shipped'
    END,
    (RANDOM() * 5000 + 100)::DECIMAL(12,2)
FROM public.customers c
CROSS JOIN generate_series(1, 3)
ON CONFLICT (order_number) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_chat_logs_user_id ON public.chat_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON public.chat_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON public.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at);
CREATE INDEX IF NOT EXISTS idx_etl_logs_job_name ON public.etl_logs(job_name);
CREATE INDEX IF NOT EXISTS idx_etl_logs_started_at ON public.etl_logs(started_at);
