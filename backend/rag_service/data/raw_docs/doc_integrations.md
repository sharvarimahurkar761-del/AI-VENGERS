# Setting up Third-Party Integrations

PulseIQ's true power is unlocked when connected to the rest of your technology stack. We offer native integrations with over 50 popular platforms, including Slack, Salesforce, Datadog, and Jira. This guide explains how to configure and manage these connections.

### Accessing the Integrations Hub
To manage your integrations, you must have Workspace Administrator privileges. Navigate to **Settings > Integrations** from the left-hand navigation menu. Here, you will see a directory of all available integrations, categorized by function (e.g., Communication, CRM, Monitoring).

### Connecting to Slack (Example)
1. In the Integrations Hub, find **Slack** under the "Communication" category and click **"Connect"**.
2. You will be redirected to Slack's authorization page. Review the permissions PulseIQ is requesting (primarily permission to post messages to channels).
3. Select the Slack channel where you want PulseIQ alerts to be sent, and click **"Allow"**.
4. You will be redirected back to PulseIQ. The Slack integration status will now show as "Active".
5. Click on the gear icon next to the active Slack integration to configure alert routing. You can create rules such as: "If a Critical Error occurs, send an immediate notification to #devops-alerts".

### Webhooks and Custom Integrations
If we do not offer a native integration for your preferred tool, you can use PulseIQ Webhooks. By going to **Settings > Webhooks**, you can define custom endpoints that PulseIQ will send JSON payloads to whenever specific events occur (like a new user signup or a system outage). This allows you to build custom automations with tools like Zapier or Make.
