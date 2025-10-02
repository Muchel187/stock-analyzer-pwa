-- Migration: Add Historical Prices Tables
-- Created: October 2, 2025
-- Purpose: Store historical stock price data locally for smart caching

-- Create the historical_prices table
CREATE TABLE IF NOT EXISTS historical_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    date DATE NOT NULL,

    -- OHLCV data
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT NOT NULL,
    adjusted_close FLOAT,
    volume BIGINT,

    -- Metadata
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicates
    CONSTRAINT uq_ticker_date UNIQUE (ticker, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ticker ON historical_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_date ON historical_prices(date);
CREATE INDEX IF NOT EXISTS idx_ticker_date ON historical_prices(ticker, date);

-- Create the data_collection_metadata table
CREATE TABLE IF NOT EXISTS data_collection_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,

    -- Tracking
    last_collected_at TIMESTAMP,
    last_successful_collection TIMESTAMP,

    -- Data range
    earliest_date DATE,
    latest_date DATE,
    data_points_count INTEGER DEFAULT 0,

    -- Status
    collection_status VARCHAR(50),  -- 'success', 'failed', 'pending', 'rate_limited'
    error_message TEXT,
    consecutive_failures INTEGER DEFAULT 0,

    -- Priority (higher = more important)
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for the metadata table
CREATE INDEX IF NOT EXISTS idx_metadata_ticker ON data_collection_metadata(ticker);
CREATE INDEX IF NOT EXISTS idx_metadata_priority ON data_collection_metadata(priority);
CREATE INDEX IF NOT EXISTS idx_metadata_status ON data_collection_metadata(collection_status);

-- SQLite version (if using SQLite)
-- SQLite doesn't support SERIAL, BIGINT, or some constraints
-- Use this version if DATABASE_URL starts with sqlite:///

/*
-- SQLite Version:
CREATE TABLE IF NOT EXISTS historical_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL NOT NULL,
    adjusted_close REAL,
    volume INTEGER,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_ticker ON historical_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_date ON historical_prices(date);
CREATE INDEX IF NOT EXISTS idx_ticker_date ON historical_prices(ticker, date);

CREATE TABLE IF NOT EXISTS data_collection_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    last_collected_at DATETIME,
    last_successful_collection DATETIME,
    earliest_date DATE,
    latest_date DATE,
    data_points_count INTEGER DEFAULT 0,
    collection_status TEXT,
    error_message TEXT,
    consecutive_failures INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metadata_ticker ON data_collection_metadata(ticker);
CREATE INDEX IF NOT EXISTS idx_metadata_priority ON data_collection_metadata(priority);
CREATE INDEX IF NOT EXISTS idx_metadata_status ON data_collection_metadata(collection_status);
*/