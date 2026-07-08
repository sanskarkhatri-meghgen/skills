# Parser Reference — Per Language & Framework

## Scoped Component Parsing

**CRITICAL RULE:** All parsing and file reading MUST be scoped strictly to the **Component Path** discovered during Phase 1. Do not assume the component resides at the root of the repository. If a component was found at `repo-A/backend/`, you must look for `package.json`, `routes/`, etc. inside `repo-A/backend/`, not in the root.

## Priority Files to Read (by Component Role)

Always read these first within the component's directory — they give the most signal per token spent.

### Node.js / JavaScript / TypeScript
```
package.json               # deps reveal framework, scripts reveal build/start
src/index.ts | app.ts | server.ts | main.ts   # entry point, port, middleware
src/routes/ | src/api/     # route definitions
.env | .env.example        # env vars (use .env.example if .env not present)
docker-compose.yml         # wiring
```

**Route pattern scanning** (grep for these):
```
app.get|post|put|delete|patch(
router.get|post|put|delete|patch(
@Get|@Post|@Put|@Delete|@Patch(   # NestJS decorators
fastify.get|post|register(
```

**Outbound call patterns**:
```
fetch(|axios.|got.|request(    # HTTP calls
new Redis(|createClient(       # Redis
mongoose.connect|Sequelize(|pg.Pool|knex(   # DBs
new SQS(|new SNS(|new S3(      # AWS SDK
amqplib.connect|new Kafka(     # queues
```

### Python
```
requirements.txt | pyproject.toml | Pipfile
main.py | app.py | wsgi.py | asgi.py
routes/ | views/ | api/
.env | .env.example | config.py | settings.py
```

**Framework detection**:
- `flask` in requirements → Flask; look for `@app.route`
- `fastapi` → FastAPI; look for `@router.get`, `@app.get`
- `django` → Django; look for `urls.py`, `urlpatterns`
- `celery` → async task worker

**Outbound patterns**:
```
requests.get|post|Session(    # HTTP
psycopg2|asyncpg|sqlalchemy   # Postgres
pymongo|motor                 # Mongo
redis.Redis|aioredis          # Redis
boto3.client|resource(        # AWS
pika|aio_pika|confluent_kafka # queues
```

### Go
```
go.mod                        # module name, dependencies
main.go | cmd/*/main.go
internal/server/ | pkg/api/ | handler/
config/ | internal/config/
```

**Framework detection**: `gin-gonic/gin`, `labstack/echo`, `gorilla/mux`, `go-chi/chi`, `grpc`

**Route patterns**:
```
r.GET|POST|PUT|DELETE(
e.GET|POST(
router.Handle(
pb.Register*Server(           # gRPC service registration
```

**Outbound patterns**:
```
http.NewRequest|http.Get      # HTTP
database/sql|gorm|sqlx        # DB
redis.NewClient(              # Redis
aws-sdk-go                    # AWS
```

### Java / Kotlin (Spring Boot)
```
pom.xml | build.gradle
src/main/java/**/Application.java
src/main/java/**/controller/
src/main/resources/application.yml | application.properties
```

**Route patterns**: `@RestController`, `@GetMapping`, `@PostMapping`, `@RequestMapping`

**Outbound**: `RestTemplate`, `WebClient`, `@FeignClient`, `JpaRepository`, `KafkaTemplate`, `RedisTemplate`

### Rust
```
Cargo.toml                    # deps reveal framework
src/main.rs | src/lib.rs
src/routes/ | src/handlers/
```

**Frameworks**: `actix-web`, `axum`, `warp`, `rocket`

---

## Terraform Parsing

### Key files to read
```
main.tf | provider.tf        # provider config, region
variables.tf                 # input variables
outputs.tf                   # exported values
*.tf in modules/             # reusable modules
terraform.tfvars | *.auto.tfvars  # actual values
backend.tf                   # remote state
```

### Resource extraction patterns

**Compute**:
```hcl
resource "aws_instance"         # EC2
resource "aws_ecs_service"      # ECS
resource "aws_eks_cluster"      # EKS
resource "google_compute_instance"
resource "azurerm_virtual_machine"
```

**Networking**:
```hcl
resource "aws_vpc"
resource "aws_subnet"
resource "aws_security_group"   # check ingress rules for 0.0.0.0/0 — security issue
resource "aws_lb" | "aws_alb"
resource "aws_route53_record"
resource "aws_cloudfront_distribution"
```

**Data**:
```hcl
resource "aws_db_instance"      # RDS — note engine, instance_class, multi_az
resource "aws_elasticache_cluster"
resource "aws_s3_bucket"        # check acl = "public-read" — security issue
resource "aws_dynamodb_table"
```

**Messaging**:
```hcl
resource "aws_sqs_queue"
resource "aws_sns_topic"
resource "aws_msk_cluster"      # Kafka
```

**IAM (check for over-permissive)**:
```hcl
resource "aws_iam_role"
resource "aws_iam_policy"       # check for Action: "*" or Resource: "*"
```

### Issue signals in Terraform
- `ingress { cidr_blocks = ["0.0.0.0/0"] }` on port 22, 3306, 5432, 27017 → Critical security
- `publicly_accessible = true` on RDS → High security
- `acl = "public-read"` or `"public-read-write"` on S3 → Critical security
- `multi_az = false` on production RDS → Medium reliability
- `deletion_protection = false` on RDS → Medium reliability
- No `lifecycle { prevent_destroy = true }` on stateful resources → Low reliability
- `instance_type = "m5.4xlarge"` for dev/staging → Medium cost

---

## Docker / Docker Compose Parsing

### docker-compose.yml
Read the full file — it's usually short and contains all the wiring.

Extract:
```yaml
services:
  <name>:
    image: <image>            # or build: <path>
    ports: ["host:container"] # note exposed ports
    environment:              # env vars — service URLs here = connections
      SERVICE_URL: http://other-service:8080
    depends_on:               # startup order
    healthcheck:              # present? if absent → reliability issue
    networks:                 # shared networks = can communicate
    volumes:                  # persistent data
    deploy:
      replicas:               # if 1 for a stateful service → reliability issue
      resources:
        limits:               # if absent → reliability issue
```

### Dockerfile
```dockerfile
FROM <base>:<tag>     # note if using :latest — reliability issue
EXPOSE <port>
ENTRYPOINT / CMD      # how the app starts
ENV <key>=<value>     # hardcoded env vars — check for secrets
```

---

## Kubernetes Parsing

### Files to scan
```
k8s/*.yaml | manifests/*.yaml | helm/templates/*.yaml
```

### Extract from Deployments
```yaml
spec:
  replicas:              # 1 for critical service → reliability
  template:
    spec:
      containers:
      - image:           # :latest tag → reliability issue
        resources:
          requests:      # absent → reliability issue
          limits:        # absent → reliability issue
        livenessProbe:   # absent → reliability issue
        readinessProbe:  # absent → reliability issue
        env:
        - name: SECRET
          value: "hardcoded"   # NEVER do this → critical security
```

### Extract from Services
```yaml
kind: Service
spec:
  type: LoadBalancer | ClusterIP | NodePort
  ports:
  - port: / targetPort:
```

### Extract from Ingress
```yaml
kind: Ingress
spec:
  tls:                   # absent → reliability/security issue
  rules:
  - host:
    http:
      paths:
      - path:
        backend:
          service:
            name:        # maps to a Service name
```

---

## Environment Variable Conventions

Env vars are the primary cross-service wiring mechanism. When you see these patterns, infer a dependency:

| Pattern | Inferred connection |
|---------|-------------------|
| `*_URL`, `*_HOST`, `*_ENDPOINT` | HTTP service call |
| `*_DATABASE_URL`, `*_DB_HOST` | Database connection |
| `*_REDIS_URL`, `*_REDIS_HOST` | Redis connection |
| `*_QUEUE_URL`, `*_TOPIC_ARN` | Queue/pub-sub |
| `*_API_KEY`, `*_SECRET`, `*_TOKEN` | External API |
| `JWT_SECRET`, `AUTH_SECRET` | Auth configuration |

When a value matches another service's name (e.g. `USER_SERVICE_URL=http://users:8080` and there's a service named `users`), mark as **confirmed connection**. When a value is a template `${USER_SERVICE_URL}` with no concrete value visible, mark as **inferred connection**.