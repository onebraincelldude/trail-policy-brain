# policy-brain
Governed context layer for company-knowledge agents: policy snippets carry source rule IDs,
and every claim in an agent's answer must cite a rule that was actually retrieved for that
question. Uncited claims and citations to non-retrieved rules both fail. Gates in
`cases.json`; any agent callable via `python run.py my_agent.py` (exposing
`run(question)` returning answer, claims, citations). `python run.py` runs the naive demo
agent, which the eval blocks.
