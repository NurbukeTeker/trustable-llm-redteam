import json
p="prompts\\injection_prompts.json"
data=json.load(open(p,encoding="utf-8"))
open("prompts\\tmp_prompts.json","w",encoding="utf-8").write(json.dumps(data[:2],ensure_ascii=False,indent=2))
print("Wrote prompts\\tmp_prompts.json with", len(data[:2]), "prompts")