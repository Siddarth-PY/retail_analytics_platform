import asyncio

async def process_daily_sales(tenant_id):
    print(f"START background job for tenant {tenant_id}", flush=True)
    await asyncio.sleep(2)  # simulate work so we can see it
    print(f"FINISHED background job for tenant {tenant_id}", flush=True)