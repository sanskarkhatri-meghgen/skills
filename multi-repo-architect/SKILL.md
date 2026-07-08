---
name: multi-repo-architect
description: >
  Use this skill whenever a user provides multiple repositories (frontend, backend, infrastructure, Terraform, Docker, Kubernetes, deployment configs, etc.) and wants to understand the overall system, generate architecture documentation, create architecture diagrams, identify issues/risks, or ask questions about how the system fits together. Trigger this skill when the user says things like: "analyze my repos", "understand my system", "generate architecture docs", "draw me an architecture diagram", "what's wrong with my infrastructure", "explain how these services connect", or provides GitHub URLs / zip files / local paths for 2+ repositories. Also trigger for single repos when the user explicitly asks for architecture analysis, diagrams, or system-wide issue detection.
---

# Multi-Repo Architect Skill

Ingest multiple repositories and build a unified architectural model. There are 4 possible deliverables:

**CRITICAL**: Every time this skill is activated, you MUST first ask the user which of the following 4 deliverables they want you to generate. Do NOT generate all 4 by default.

1. `architecture.md` — narrative documentation of the system
2. `low-level-diagram.drawio` — logical service map (with service/vendor logos wherever possible)
3. `high-level-diagram.drawio` — cloud architecture map (with vendor icons)
4. `issues.md` — issues report with severity ratings (Security / Reliability / Cost)

After generating the requested deliverables, stay interactive — answer follow-up questions using the model you built.

---

## Phase 1 — Intake & Role Inference

### Accepting Repos

**IMPORTANT**: If only ONE repository is provided or found during intake, you MUST explicitly ask the user if there are other repositories they want to include as well before you proceed.

Handle all three input modes. They may be mixed in the same request.

**A. Uploaded zip files**
```bash
ls /mnt/user-data/uploads/          # list uploaded files
unzip <file>.zip -d /tmp/repos/<name>/
```

**B. Local paths (user pastes a path)**
```bash
ls <path>
find <path> -type f | head -100
```

**C. GitHub / GitLab URLs**
- If user provides a token: include `Authorization: Bearer <token>` header in all fetch calls
- Without token: fetch raw content via `raw.githubusercontent.com` or GitLab raw URLs
- Use GitHub API to list repo contents: `https://api.github.com/repos/<owner>/<repo>/git/trees/HEAD?recursive=1`
- Fetch individual files: `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`
- If rate-limited without a token, tell the user and ask for one

### Component Discovery & Role Inference

Instead of trying to assign a single role to an entire repository (which fails for monorepos or repos with co-located infrastructure code), you MUST perform a **static analysis of the directory tree** to discover logical **Components**.

1. **Scan the directory tree** of each repository.
2. **Identify Component Boundaries**: A boundary is a directory that acts as the root of a logical service or module. This is typically indicated by a primary configuration, dependency, build, or entrypoint file.
3. **Handle Co-located Files**: If a single directory contains multiple boundary signals (e.g., both a `package.json` for a backend AND `.tf` files for its deployment infrastructure in the exact same directory), treat it as **ONE component** with a combined role (e.g., `backend + infrastructure`). Do not artificially split components if they share the same directory path.
4. **Infer the Role per Component**, not per repository. 

| Boundary Signal (Look for these in the directory) | Inferred Component Role |
|--------|--------------|
| `package.json` (with react/vue/angular), OR `index.html` with `js/`/`css/` dirs (vanilla) | **frontend** |
| `package.json` (with express/fastify), `go.mod`, `requirements.txt`, `pom.xml`, OR standalone `main.go`/`app.py` | **backend-service** |
| `main.tf`, `*.tf` files | **infrastructure (Terraform)** |
| `docker-compose.yml`, `docker-compose.yaml` | **orchestration** |
| `Dockerfile` only (when no explicit app build files are found) | **containerized-service** (role TBD from app code) |
| `k8s/`, `kubernetes/`, `manifests/`, `helm/` | **kubernetes** |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` | **ci-cd** |
| `nginx.conf`, `traefik.yml`, `haproxy.cfg` | **gateway/proxy** |

> **⚠️ Deterministic Execution:** The discovery of components must be strict and static. Rely on concrete signals (the boundary files) rather than guessing. If a directory doesn't have a clear boundary file but seems important, investigate it statically by reading its configs. 

**Announce what you found** before deep-parsing:
> "I scanned X repos and discovered Y distinct components. Here's how I've classified them: [table mapping Repo & Component Path -> Role]. Does this look right?"

Wait for confirmation only if there's genuine ambiguity. Otherwise proceed.

---

## Phase 2 — Deep Parse

Read the reference file for the relevant component type. For each repo, apply the appropriate parser strategy from `references/parsers.md`.

**Quick summary of what to extract per role:**

### frontend
- Framework (React/Vue/Next/Angular/etc.)
- Build tooling (Vite, Webpack, CRA)
- API base URLs / env vars pointing to backends (`REACT_APP_API_URL`, `VITE_API_BASE`, etc.)
- Auth method (OAuth redirect URLs, JWT storage)
- External services called (analytics, feature flags, CDN)

### backend-service
- Language + framework
- HTTP routes exposed (look in route files, controllers, main entry)
- Outbound calls: other services (URLs in env vars, hardcoded hostnames, service discovery), DBs (connection strings), queues (SQS, RabbitMQ, Kafka topic names), external APIs
- Environment variables consumed — these are the dependency interface
- Auth mechanisms (JWT validation, API keys, OAuth)

### infrastructure (Terraform)
- Provider(s) and region(s)
- Key resources: VPCs, subnets, security groups, EC2/ECS/EKS, RDS/Aurora, S3, SQS/SNS, ALB/NLB, CloudFront, Route53, IAM roles
- Modules used (local or registry)
- Outputs (exposed values — often consumed by app layer)
- Remote state backend

### orchestration (docker-compose)
- Service list, image/build source
- Port mappings (host:container)
- Networks and which services share them
- Volumes
- `depends_on` and `healthcheck`
- Env var values (especially service URLs — these reveal inter-service wiring)

### kubernetes
- Deployments / StatefulSets: image, replicas, resource requests/limits
- Services: ClusterIP vs LoadBalancer vs NodePort, ports
- Ingress: hostnames, paths, backend service routing
- ConfigMaps / Secrets referenced
- Namespaces

### ci-cd
- Trigger conditions (push to main, PR, tag)
- Build steps (test, lint, build, push image)
- Deploy steps (kubectl apply, helm upgrade, terraform apply, etc.)
- Target environments

> **⚠️ The roles and extraction lists above are NOT exhaustive.** Real-world repos contain technologies, frameworks, patterns, and resource types not listed here. If you encounter something unfamiliar (e.g., Pulumi instead of Terraform, Dagger pipelines, Bazel builds, serverless frameworks, data pipeline orchestrators like Airflow/Prefect, ML frameworks, etc.), **research it yourself** — read the code, understand what it does, and extract the relevant architectural information. The `references/parsers.md` file is similarly a starting point, not a complete reference. Use your own knowledge to fill gaps. Never assume something is unimportant just because it isn't mentioned here.

---

## Phase 3 — Unified Model Assembly

After parsing all repos, build a mental model structured like this (keep it in context, don't write it to disk — it's working memory):

```
SystemModel {
  services: [
    {
      name: string,
      role: frontend | backend | gateway | worker | scheduler,
      repo: string,
      component_path: string,
      language: string,
      framework: string,
      exposes: [ { protocol, port, path_prefix } ],
      calls: [ { target: service_name_or_url, protocol, purpose } ],
      databases: [ { type, name, how_connected } ],
      queues: [ { type, name, producer|consumer } ],
      external_apis: [ string ],
      env_vars: [ string ],
      containerized: bool,
      docker_image: string,
    }
  ],
  datastores: [ { name, type (postgres|mysql|redis|mongo|s3|dynamo), managed_by } ],
  queues: [ { name, type, producers: [], consumers: [] } ],
  infra: {
    component_paths: [ string ],
    provider: aws|gcp|azure|multi,
    region: string,
    vpc: { cidr, subnets: [] },
    compute: [ { type, name, sizing } ],
    managed_services: [ string ],
    load_balancers: [ { name, type, targets: [] } ],
  },
  external_dependencies: [ string ],
  ingress_points: [ { hostname, tls: bool, routes_to: service } ],
  ci_cd: { platform, environments: [], deploy_strategy }
}
```

**Cross-component resolution**: match env var values to service names. For example, if `payments-service` has `USER_SERVICE_URL=http://users:8080` and there's a Docker service named `users` — these are connected. Build the edges.

---

## Phase 4 — Generate Outputs

Generate all four files. Read `references/output-templates.md` for the exact structure of each.

### 4a. architecture.md

Sections:
1. **System Overview** — what the system does (infer from service names and routes), tech stack summary, team-facing description
2. **Services** — one subsection per service: role, tech, what it exposes, what it depends on
3. **Data Architecture** — datastores, who owns what, data flow
4. **Infrastructure** — cloud provider, key resources, networking topology
5. **Inter-Service Communication** — the wiring: who calls whom, sync vs async
6. **Deployment & CI/CD** — how things get built and deployed
7. **External Dependencies** — third-party APIs, SaaS services

### 4b. Architecture Diagrams

Generate two `.drawio` (XML) files based on `references/diagram-guide.md`:

1. **`low-level-diagram.drawio`**: A detailed Service Map showing all logical connections. **Use relevant service/vendor logos wherever possible** (e.g., Pub/Sub, BigQuery, Redis, Dataflow icons). Fall back to basic shapes (rectangles, cylinders) only when no logo exists for a component.
2. **`high-level-diagram.drawio`**: A Cloud Infrastructure view showing VPCs, Gateways, and high-level topology. **You must use relevant vendor icons/logos** (e.g., AWS EC2 icon, GCP GKE icon).

**IMPORTANT: Using Logos/Icons in Diagrams**
Both diagrams MUST use recognizable service logos wherever possible. See `references/diagram-guide.md` Section 3 for the full icon reference table. Key rules:
- **GCP services**: Use `shape=mxgraph.gcp2.{ShapeName}` (stencil-based). Example:
```xml
<mxCell id="bq_id" value="BigQuery" style="shape=mxgraph.gcp2.BigQuery;html=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="130" height="100" as="geometry" />
</mxCell>
```
- **AWS services**: Use `shape=image` with `image=img/lib/aws4/...` paths (SVG image-based).
- **Generic (K8s, Redis, Docker)**: Use `shape=image` with `image=img/lib/mscae/...` paths.

> **⚠️ The icon reference table in `references/diagram-guide.md` is NOT exhaustive.** It covers common services, but draw.io has thousands of icons across many stencil libraries. If you need an icon not listed (e.g., Azure services, Cloudflare, Terraform, Vault, Consul, Snowflake, Databricks, etc.), **look it up yourself** — draw.io stencil libraries include `img/lib/azure2/`, `img/lib/aws4/`, `img/lib/mscae/`, and many more. Use your knowledge of draw.io's stencil paths to find the right icon. If you truly can't find an icon, then fall back to a clearly labeled plain shape.

Only fall back to plain shapes (rectangles, cylinders) when no logo exists for a component.

**IMPORTANT: Generating the Draw.io Link**
After generating the `.drawio` files, you MUST provide the user with a direct, editable `app.diagrams.net` link for both diagrams.
Use the helper script bundled with this skill with the `--auto` flag (auto-detects required libraries like `gcp2` or `aws4` from the XML):

```bash
python3 <skill_root>/scripts/gen_drawio_url.py low-level-diagram.drawio --auto
python3 <skill_root>/scripts/gen_drawio_url.py high-level-diagram.drawio --auto
```

If the script is not accessible, use this equivalent one-liner (note: MUST use a SINGLE compressor instance via variable `c`, and MUST include `?libs=gcp2` for GCP diagrams):
```bash
python3 -c "import sys,zlib,base64,urllib.parse; xml=open('low-level-diagram.drawio').read(); c=zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,zlib.DEFLATED,-15); compressed=c.compress(urllib.parse.quote(xml,safe='').encode('utf-8'))+c.flush(); print('https://app.diagrams.net/?libs=gcp2#R'+base64.b64encode(compressed).decode('utf-8'))"
```
Provide the resulting URLs directly to the user in your response.

### 4c. issues.md

For each issue found during parsing:

```markdown
### [SEVERITY] Issue Title
- **Category**: Security | Reliability | Cost
- **Affected**: service-name or resource-name
- **Description**: what the problem is
- **Evidence**: the specific file/line/config that reveals it
- **Recommendation**: concrete fix
```

Severity levels:
- 🔴 **Critical** — active exploit risk or guaranteed failure under load
- 🟠 **High** — significant risk, should fix before production
- 🟡 **Medium** — worth addressing, not urgent
- 🔵 **Low** — best practice improvement

**Security checks**: hardcoded secrets in env files committed to repo, open security groups (`0.0.0.0/0` on sensitive ports), missing auth on routes, HTTP (not HTTPS) internal calls, overly permissive IAM roles, publicly accessible S3 buckets

**Reliability checks**: no health checks on Docker/K8s services, single replica for critical services, no retry/circuit breaker evident in service calls, missing resource limits in K8s, no DB connection pooling, synchronous chains that create cascading failure risk

**Cost checks**: oversized instance types for apparent workload, no auto-scaling configured, unused resources (security groups with no attachments, unattached EBS, etc.), data transfer across AZs in hot paths

> **⚠️ These check lists are NOT exhaustive.** They are common patterns to look for, but every codebase has unique risks. Apply your own security, reliability, and cost expertise to identify issues specific to the technologies in the repos. For example: missing CORS configuration, insecure deserialization, lack of rate limiting, missing backup strategies, unencrypted data at rest, deprecated dependencies with known CVEs, missing audit logging, etc. If you see something that looks wrong but isn't in these lists, **report it anyway**.

---

## Phase 5 — Interactive Q&A

After delivering the three files, tell the user:

> "I've built a full model of your system. Ask me anything — 'what calls the payments service?', 'which services have no health checks?', 'what would break if Redis went down?', 'how does a user login request flow through the system?'"

Answer from the unified model you built in Phase 3. Be specific — name services, files, line numbers where relevant. If you're uncertain about something (e.g. a connection that was implied but not explicit), say so.

---

## Important Behaviours

- **Nothing in this skill is a comprehensive list**: Every table, checklist, icon reference, parser pattern, role list, and issue signal in this skill and its reference files is a **starting point, not a boundary**. If you encounter technologies, patterns, resource types, or issues not mentioned anywhere in this skill, **you are expected to handle them using your own knowledge**. Investigate independently, read the code, and figure it out. Do not skip, ignore, or gloss over things just because they aren't explicitly listed.
- **Ask when in doubt, never assume**: If you genuinely don't understand something after investigating, **ask the user** rather than making assumptions. This applies to repo roles, technology choices, architectural patterns, icon selection, issue severity — everything. It's always better to ask a clarifying question than to guess wrong.
- **Be transparent about confidence**: if you inferred something (e.g. "payments-service probably calls users-service based on the env var `USER_SERVICE_URL`"), say "inferred" vs "confirmed"
- **Don't hallucinate services**: only include what you actually found in the code/config
- **Scale your reading**: for large files (>500 lines), read the top (imports, config) and scan for key patterns (route definitions, DB calls) rather than reading every line
- **Announce progress**: for medium-scale inputs this takes time. Tell the user what you're doing ("Parsing Terraform... found 3 RDS instances, 1 VPC...")
- **One confirmation gate**: the only time you pause for user input after starting is if role inference is ambiguous. Everything else runs to completion.

---

## Reference Files

- `references/parsers.md` — detailed per-language/framework parsing patterns
- `references/diagram-guide.md` — SVG drawing instructions, layout, colors
- `references/output-templates.md` — exact structure for all three output files