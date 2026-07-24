import subprocess, json, base64

def gh(p):
    r = subprocess.run(["gh", "api", p], capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else {}

d = gh("repos/ledi13035/MINISO-AI-Product-Genome/contents/agents/design_agent.py")
content = base64.b64decode(d["content"]).decode("utf-8", "ignore")
print("SEASONS present:", "SEASONS" in content)
print("COBRANDS present:", "COBRANDS" in content)
print("season field:", "season: str" in content)

for p in ["web/app.py", "web/templates/index.html", "web/templates/report.html"]:
    e = gh("repos/ledi13035/MINISO-AI-Product-Genome/contents/" + p)
    print(p, "->", "OK" if "sha" in e else "MISSING")

c = gh("repos/ledi13035/MINISO-AI-Product-Genome/commits?per_page=1")[0]
print("latest:", c["sha"][:10], "|", c["commit"]["message"].split("\n")[0])
