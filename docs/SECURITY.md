# NyayaSaathi AI — Security & Responsible AI Policy

## 1. Zero Trust for User Uploads
- **Isolation**: Uploaded user invoices, emails, receipts, and order confirmations are stored in tenant-isolated paths (`data/uploads/{case_id}/`) and analyzed transiently.
- **No Global Indexing**: User documents are strictly excluded from Qdrant vector collections and BM25 indexes. The public legal knowledge base consists solely of official gazettes and statutory enactments.
- **Sanitization**: Filenames are sanitized, MIME types are verified using byte magic numbers (not solely file extensions), and uploads are restricted to a maximum of 15MB.

---

## 2. API Key Protection & Server-Side Execution
- LLM API keys (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`) and database credentials exist strictly server-side.
- The Next.js frontend interacts solely with the FastAPI backend via proxy REST endpoints and never touches LLM credentials.
- Error handlers sanitize exceptions and never expose raw stack traces, database schemas, or internal configuration keys to API consumers.

---

## 3. Responsible AI & Legal Disclaimers
1. **Informational Boundary**: NyayaSaathi AI is an assistive research and grievance drafting tool. It clearly states to users that it does not provide formal legal representation or judicial determination.
2. **Defamation & Unsubstantiated Claims**: The assistant phrases liability findings conditionally (e.g., 'This conduct may constitute an unfair trade practice under Section 2(47)...' rather than 'The company has violated the law').
3. **No Automatic Filing**: NyayaSaathi AI drafts complaints and procedural checklists for the user. It never automatically files cases or makes unverified submissions to courts or helplines.
