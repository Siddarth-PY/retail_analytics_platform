# retail_analytics_platform
Multi-Tenant Retail Analytics Platform
Overview
This project implements a production-style backend system for a retail analytics platform supporting multiple tenants securely.
The system ingests orders, tracks inventory snapshots, and provides analytics such as profitability, demand trends, and inventory depletion.
The platform is designed using clean architecture principles and supports asynchronous operations for high performance.

Backend Framework
  -FastAPI
Databases
 -PostgreSQL → transactional data
 -MongoDB → analytics snapshots
Other Technologies
SQLAlchemy Async ORM
 -Motor (Async MongoDB driver)
 -JWT Authentication
 -Docker & Docker Compose
 
 Architecture Diagram:

                +-------------------+
                |       Client      |
                |  (Swagger / API)  |
                +---------+---------+
                          |
                          v
                +-------------------+
                |       FastAPI     |
                |   REST API Layer  |
                +---------+---------+
                          |
            +-------------+-------------+
            |                           |
            v                           v
    +-------------------+        +-------------------+
    |    PostgreSQL     |        |      MongoDB      |
    | Transaction Data  |        |  Analytics Data   |
    +-------------------+        +-------------------+
            |
            v
    +-------------------+
    | Orders / Products |
    | Users / Tenants   |
    +-------------------+


Database Schema



             +----------------+
             |    Tenants     |
             |----------------|
             | id (PK)        |
             | name           |
             +-------+--------+
                     |
                     |
             +-------v--------+
             |     Users      |
             |----------------|
             | id (PK)        |
             | tenant_id (FK) |
             | email          |
             +----------------+

             +----------------+
             |    Products    |
             |----------------|
             | id (PK)        |
             | tenant_id (FK) |
             | name           |
             | sku            |
             +-------+--------+
                     |
                     |
             +-------v--------+
             | ProductPrices  |
             |----------------|
             | id (PK)        |
             | product_id(FK) |
             | cost_price     |
             | selling_price  |
             +----------------+

             +----------------+
             |     Orders     |
             |----------------|
             | id (PK)        |
             | tenant_id (FK) |
             | revenue        |
             | profit         |
             +-------+--------+
                     |
                     |
             +-------v--------+
             |   OrderItems   |
             |----------------|
             | id (PK)        |
             | order_id (FK)  |
             | product_id(FK) |
             | quantity       |
             +----------------+



#Layer Responsibilities

Routers
 -Handle HTTP requests and responses.
Services
 -Contain business logic.
Repositories
 -Handle database queries.
Models
 -Define database schema.
Schemas
 -Validate request and response data.
Dependencies
 -Provide authentication and database access.

Key Design Decisions
 UUID primary keys
 Foreign key relationships
 Composite unique constraints
 Indexed fields for performance
 Transactions for order creation
 Idempotency key for duplicate request protection
  UniqueConstraint("tenant_id", "sku") Ensures product SKU uniqueness per tenant.

MongoDB (Analytics Storage)
 MongoDB is used for:
 Inventory Snapshots
 Daily Sales Aggregation
 Cached KPI Metrics
 MongoDB is more efficient for these workloads compared to relational storage.

Example collection:
inventory_snapshots
Feilds
tenant_id
product_id
quantity
snapshot_date

Multi-Tenant Isolation
Tenant security is enforced using JWT authentication.
JWT payload contains:
user_id
tenant_id
role

All Database queries filter by tenant_id this prevents the cross-tenant data leakage
 Example: WHERE tenant_id = :tenant_id


Implemented APIs
Authentication

POST /auth/login

Returns JWT token containing tenant information.

Order Ingestion

POST /orders

Features:

accepts multiple order items

transactional order creation

revenue and profit calculation

idempotency protection

Example request:
 {
  "idempotency_key": "order123",
  "items": [
    {
      "product_id": "...",
      "quantity": 2
    }
  ]
}
Inventory Snapshot

POST /inventory/snapshot

Stores daily inventory snapshot in MongoDB.

Profitability Analytics

GET /analytics/profitability

Returns:

revenue

cost

gross profit

gross margin %

Uses optimized SQL aggregation.

Demand Trend

GET /analytics/demand-trend

Provides:

daily sales

year-over-year comparison

growth percentage

Inventory Depletion

GET /analytics/inventory-depletion

Combines:
 MongoDB inventory snapshots
 PostgreSQL sales velocity
 Returns estimated days to stock-out.
 
 Background Processing:
 Background processing is implemented using FastAPI BackgroundTasks.
 After order creation, a background task triggers analytics recomputation.

Why BackgroundTasks instead of Celery?
simpler deployment
no external message broker required
suitable for assignment scale

Query Optimization

The analytics APIs rely on database-side aggregation instead of processing large datasets in Python.

Profitability Query
SELECT
SUM(total_revenue),
SUM(total_cost)
FROM orders
WHERE tenant_id = ?
AND created_at BETWEEN ? AND ?

This allows the database engine to efficiently compute revenue and profit.

Demand Trend Query

SELECT DATE(created_at), SUM(total_revenue)

FROM orders

GROUP BY DATE(created_at)

Used to generate daily sales trends and year-over-year comparisons.

Index Strategy

Indexes were added to improve query performance.

PostgreSQL

(tenant_id, created_at)      → analytics queries
(product_id, effective_from) → latest price lookup
(order_id, product_id)       → order item joins

MongoDB

(product_id, snapshot_date)

This index enables fast retrieval of the latest inventory snapshot.

Running the Application
Start Services
docker compose up --build

Services started:

FastAPI

PostgreSQL

MongoDB

Testing APIs

Swagger UI:

http://localhost:8000/docs

Steps:

Call /auth/login

Copy JWT token

Click Authorize

Use APIs
Method	Endpoint	Description

POST	/auth/login	Generate JWT token

POST	/orders	Create order

POST	/inventory/snapshot	Store inventory snapshot

GET	/analytics/profitability	Revenue & profit analytics

GET	/analytics/demand-trend	Daily sales trend

GET	/analytics/inventory-depletion	Estimate stock-out





