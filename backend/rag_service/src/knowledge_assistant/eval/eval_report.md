# Knowledge Assistant Evaluation Report

## Summary Statistics

### Category: Answerable
- **Queries**: 4
- **Grounded Rate**: 100.0%
- **Hallucination Rate**: 0.0%
- **Avg Confidence**: 0.91

### Category: Borderline
- **Queries**: 3
- **Grounded Rate**: 100.0%
- **Hallucination Rate**: 0.0%
- **Avg Confidence**: 0.59

### Category: Unanswerable
- **Queries**: 3
- **Grounded Rate**: 100.0%
- **Hallucination Rate**: 0.0%
- **Avg Confidence**: 0.54

### Overall
- **Total Queries**: 10
- **Overall Grounded Rate**: 100.0%
- **Overall Hallucination Rate**: 0.0%
- **Overall Avg Confidence**: 0.70

## Detailed Results

### Q: How do I hook up my account to Slack so I can get alerts there? (answerable)
**Confidence:** 0.90

**Response:**
> To connect your PulseIQ account to Slack and receive alerts, you can follow these steps: 
> 
> 1. Navigate to **Settings > Integrations** from the left-hand navigation menu, as described in [Setting up Third-Party Integrations].
> 2. Find **Slack** under the "Communication" category and click **"Connect"**.
> 3. You will be redirected to Slack's authorization page, where you should review the permissions PulseIQ is requesting.
> 4. Select the Slack channel where you want PulseIQ alerts to be sent and click **"Allow"**.
> 5. After being redirected back to PulseIQ, the Slack integration status should show as "Active".
> 6. Click on the gear icon next to the active Slack integration to configure alert routing, allowing you to create rules for when notifications are sent to your specified Slack channel.
> 
> This process is outlined in more detail in [Setting up Third-Party Integrations], specifically in the section "Connecting to Slack (Example)".

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer directly follows the steps outlined in the provided context under 'Connecting to Slack (Example)' without introducing any unsupported claims or external information.

---

### Q: I'm a DevOps engineer, can I drag and drop stuff on the UI to see my error rates? (answerable)
**Confidence:** 0.90

**Response:**
> According to [Understanding the PulseIQ Dashboard], the PulseIQ Dashboard has a modular architecture and allows customization. Every widget on the dashboard can be resized or moved using a drag-and-drop interface. 
> 
> To view error rates, you can look at the Overview Ribbon, which displays top-level metrics, including the System Error Rate. This metric is color-coded based on custom threshold settings. 
> 
> Additionally, you can add new widgets to the dashboard by clicking the "+ Add Widget" button in the bottom right corner to create a customized view that suits your needs as a DevOps engineer.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer is supported by the provided context, specifically the sections 'Understanding the PulseIQ Dashboard' and 'Customizing Your View', which describe the dashboard's modular architecture, drag-and-drop interface, and the Overview Ribbon's display of system error rates.

---

### Q: My REST API export keeps failing with a 504 Gateway Timeout error for 60 day periods, what's wrong? (answerable)
**Confidence:** 0.95

**Response:**
> According to [support_log_1029 | Title: Support Ticket #1029 Resolution Log], the issue you're experiencing with the REST API export failing with a `504 Gateway Timeout` error for large date ranges is likely due to the database query taking too long to execute. Specifically, the lack of a composite index on the events table can cause the database engine to perform a full table scan, leading to timeouts.
> 
> As described in the resolution steps of [support_log_1029], the root cause of this issue is the absence of a composite index on `(workspace_id, timestamp)` in the events table. To resolve this, you can either implement the immediate workaround suggested, which is to break your API requests into smaller chunks (e.g., 7-day chunks), or wait for a permanent fix to be implemented by the engineering team, such as the one described in [support_log_1029] where a database migration script was created to add the missing composite index.
> 
> It's also worth noting that [support_log_1029] mentions that this issue started occurring after the database grew past 500,000 records, which might be relevant to your situation. However, without more specific information about your database size and configuration, it's difficult to provide a more tailored solution. 
> 
> For a more general understanding of how to export data, you can refer to [faq_export_data | Title: FAQ: How to Export Your Data], but this document does not specifically address the technical issue you're facing with the REST API and large date ranges.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer is grounded because it directly references and explains information from the provided context, specifically support ticket #1029, without introducing unsupported claims or guessing.

---

### Q: I need to dump out all my logs into a CSV or PDF for compliance, how? (answerable)
**Confidence:** 0.90

**Response:**
> To export all your logs for compliance purposes, you can follow these steps as outlined in [FAQ: How to Export Your Data]. 
> 
> If you are an Administrator, you can perform a bulk export of your entire account data by going to **Settings > Workspace > Data Management** and clicking on **"Request Full Export"**. You will then be prompted to verify your identity using two-factor authentication (2FA). The system will compile a compressed `.zip` archive containing all JSON logs, but it does not explicitly mention CSV or PDF for this bulk export method. However, for a specific dashboard view, you can export data in CSV or PDF format.
> 
> For a more tailored export, such as CSV or PDF, you might consider exporting from a specific dashboard view that contains the logs you need. To do this, navigate to the desired dashboard, adjust the date range filters, click the **"Export"** button, and select your preferred format: **CSV**, **JSON**, or **PDF report**. 
> 
> Please note that for larger datasets, the system may process the request in the background and send you an email with a download link once it is ready.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer is supported by the provided context, specifically the FAQ section on exporting data, and does not introduce any information not present in the context.

---

### Q: Can I integrate with Microsoft Teams? (borderline)
**Confidence:** 0.90

**Response:**
> According to [Setting up Third-Party Integrations], PulseIQ offers native integrations with over 50 popular platforms, but it does not explicitly mention Microsoft Teams as one of the integrated platforms. However, it does mention that if a native integration is not available, you can use PulseIQ Webhooks to define custom endpoints and build custom automations with tools like Zapier or Make. Therefore, while there may not be a native integration with Microsoft Teams, you may still be able to integrate with it using Webhooks.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer is supported by the context, which mentions native integrations with specific platforms and the possibility of using Webhooks for custom integrations.

---

### Q: How do I create a custom widget for the dashboard? (borderline)
**Confidence:** 0.25

**Response:**
> I do not have enough information to answer that. The provided context does not contain instructions on how to create a custom widget for the dashboard. It only mentions that every widget on the dashboard can be resized or moved using a drag-and-drop interface and that you can add new widgets by clicking the "+ Add Widget" button, but it does not provide details on creating custom widgets.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer states it does not have enough information, which is supported by the context.

---

### Q: What is the specific 2FA app I need to use to verify my identity for a full export? (borderline)
**Confidence:** 0.62

**Response:**
> I do not have enough information to answer that. The provided context only mentions that you will be prompted to verify your identity using two-factor authentication (2FA) for a full export, but it does not specify the particular 2FA app required [FAQ: How to Export Your Data].

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer explicitly states it cannot provide the specific 2FA app, which is consistent with the provided context that only mentions the use of 2FA without specifying an app.

---

### Q: How much does the Enterprise Tier cost? (unanswerable)
**Confidence:** 0.62

**Response:**
> I do not have enough information to answer that. The provided context does not mention the pricing of the Enterprise Tier or any other tier. [support_log_1029] only mentions that the customer, Acme Corp, is an Enterprise Tier customer, but it does not provide any information about the cost.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer states it does not have enough information to answer the question, which is supported by the context as there is no mention of pricing for the Enterprise Tier.

---

### Q: Can I pay using a wire transfer or just credit cards? (unanswerable)
**Confidence:** 0.25

**Response:**
> I do not have enough information to answer that. The provided context does not contain information about payment methods.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer explicitly states it cannot answer due to lack of information in the provided context.

---

### Q: Does PulseIQ have a mobile app for iOS? (unanswerable)
**Confidence:** 0.75

**Response:**
> I do not have enough information to answer that. The provided context documents ([Understanding the PulseIQ Dashboard], [FAQ: How to Reset Your Password], [Setting up Third-Party Integrations]) do not mention a mobile app for iOS.

**Grounded:** True | **Hallucination:** False
**Reason:** The LLM's answer is grounded because it explicitly states it cannot answer the question due to lack of information in the provided context, and does not make any unsupported claims or provide unverified information.

---

## Known Limitations

**Confidence Scoring Heuristic:** The current confidence score heuristic uses the presence of hedging language and citation density as a proxy for answer helpfulness. As a result, it cannot reliably distinguish between an LLM offering a genuinely helpful partial/workaround answer and an LLM merely citing a document to prove it was checked and found irrelevant. Both behaviors yield similar confidence scores (e.g. 0.55-0.75). A more accurate future fix would involve the LLM generator or judge directly outputting a helpfulness label (fully/partial/none) to drive the confidence score, rather than relying on a citation-density proxy.
