"""policy-brain: citation-discipline eval for governed company-knowledge agents.

The agent returns an answer as a list of claims, each with the rule IDs it cites. A claim
passes only if it cites at least one rule AND every cited rule was in the retrieved set
for that question (no citing rules the agent never saw). Exit 1 = eval blocks the agent.
"""
import json, sys

def load_agent(path):
    if not path:
        return demo_agent
    import importlib.util
    s = importlib.util.spec_from_file_location("agent", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.run

def demo_agent(question):
    """Naive agent: one claim cites a rule that was never retrieved, one cites nothing."""
    q = question.lower()
    if "accrue" in q or "earn" in q:
        return {"claims": [
            {"text": "You accrue 1.5 PTO days per month.", "cites": ["PTO-001"]},
            {"text": "PTO can be used after 90 days.", "cites": ["PTO-001"]}]}
    if "10 days" in q:
        return {"claims": [
            {"text": "You need manager approval for over 5 consecutive days.", "cites": ["PTO-002"]},
            {"text": "You also need security sign-off for long leave.", "cites": ["SEC-201"]}]}
    return {"claims": [{"text": "Meals are reimbursed up to Rs 500 per day with receipts.", "cites": []}]}

def main():
    spec = json.load(open("cases.json"))
    agent = load_agent(sys.argv[1] if len(sys.argv) > 1 else None)
    rules = spec["rules"]
    uncited = invalid = 0
    for c in spec["cases"]:
        out = agent(c["question"])
        retrieved = set(c["retrieved"])
        for claim in out.get("claims", []):
            cites = claim.get("cites", [])
            if not cites:
                uncited += 1
                print(f"[{c['id']}] UNCITED claim: {claim['text'][:60]}")
            bad = [r for r in cites if r not in retrieved or r not in rules]
            if bad:
                invalid += len(bad)
                print(f"[{c['id']}] INVALID citation (never retrieved or unknown rule): {bad}")
        if not any(True for cl in out.get("claims", []) if not cl.get("cites") or [r for r in cl['cites'] if r not in retrieved]):
            print(f"[{c['id']}] citations clean")
    g = spec["gates"]
    ok = uncited <= g["max_uncited_claims"] and invalid <= g["max_invalid_citations"]
    print(f"\nuncited claims {uncited} (gate {g['max_uncited_claims']}), invalid citations {invalid} (gate {g['max_invalid_citations']})")
    print("AGENT:", "PASS" if ok else "BLOCKED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
