# Support Ticket #1029 Resolution Log

**Date:** October 14, 2023
**Customer:** Acme Corp (Enterprise Tier)
**Reported By:** Jane Smith, Lead Developer
**Assigned To:** Alex Carter, L2 Technical Support

### Issue Description
The customer reported that their automated data export via the REST API was failing intermittently. Specifically, when requesting exports for date ranges larger than 30 days, the API would return a `504 Gateway Timeout` error after approximately 60 seconds. This issue started occurring after their database grew past 500,000 records.

### Investigation Steps
1. **Log Review:** Alex pulled the server logs for Acme Corp's workspace. Confirmed that requests to `/api/v2/export/events` were indeed timing out at the load balancer level, which has a hard limit of 60 seconds.
2. **Database Query Profiling:** Alex reproduced the query in a staging environment using a mock dataset of similar size. The underlying SQL query aggregating the events was taking around 75 seconds to execute, which exceeded the API timeout threshold.
3. **Root Cause Analysis:** The events table lacked a composite index on `(workspace_id, timestamp)`, causing the database engine to perform a full table scan when filtering by date for a specific workspace.

### Resolution
1. **Immediate Workaround:** Alex instructed the customer to break their API requests into smaller, 7-day chunks to prevent timeouts while a permanent fix was implemented.
2. **Permanent Fix:** The engineering team created a database migration script to add the missing composite index to the events table. This was deployed in the hotfix release v2.4.1.
3. **Verification:** Post-deployment, the same 30-day export query executed in 2.3 seconds. Customer confirmed the API was functioning normally again without chunking. Ticket closed.
