cat > docs/index.md <<'EOF'
# Chad-Airline — Audit-Grade Airline Risk & Revenue Engine

**Quantify airline revenue, disruption risk, and executive decisions using Monte-Carlo simulation.**

---

## What this is
A production-ready simulation engine that generates:
- CEO-ready Executive PDF
- Probability of loss, RAROC, stress tests
- Reproducible dashboards, charts, and audit logs

Built for **airlines, insurers, auditors, and aviation consultants**.

---

## Problems it solves
- What is the probability of loss under disruption?
- Which boarding policy minimizes denied-boarding cost?
- How does stress affect RAROC and fleet decisions?

---

## What you get
- One-command Docker demo
- Executive-grade PDF report
- CSVs, charts, and explainability logs
- Deterministic, auditable results

---

## Run a demo
```bash
docker build -t airline-edition .
docker run --rm airline-edition smoke-test
