# VoxRay AI v2.0 - Cost Estimation

**Purpose:** Budget planning for infrastructure and services

---

## 💰 Current Costs (Baseline)

### Current Deployment (v1.0)

```yaml
frontend_netlify:
  plan: Free
  bandwidth: 100 GB/month (included)
  build_minutes: 300 minutes/month (included)
  monthly_cost: $0
  limitations:
    - No custom domain SSL (using netlify.app)
    - Basic analytics only
    - 100GB bandwidth limit

backend_huggingface:
  plan: Free (Community)
  compute: Shared CPU (cold starts)
  storage: Limited
  gpu_access: No guarantee
  monthly_cost: $0
  limitations:
    - Cold starts (30-60 seconds)
    - No GPU guarantee
    - Rate limiting
    - 16GB RAM limit
    - Cannot handle high load

external_services:
  openrouter_api:
    model: Gemini 2.0 Flash
    pricing: $0.075 per 1M input tokens, $0.30 per 1M output tokens
    estimated_usage: ~50K requests/month
    avg_tokens: 500 input, 200 output per request
    monthly_cost: ~$6

  edge_tts:
    provider: Microsoft Edge TTS
    pricing: Free (rate limited)
    monthly_cost: $0

total_current_monthly: $6
🚀 Development Environment Costs
Recommended Setup for Active Development
YAML

compute:
  provider: AWS
  instance_type: g4dn.xlarge
  specs:
    - 1x NVIDIA T4 GPU (16GB)
    - 4 vCPUs
    - 16 GB RAM
  pricing:
    on_demand: $0.526/hour
    reserved_1yr: $0.316/hour (40% savings)
  usage_pattern: 8 hours/day, 20 days/month
  monthly_hours: 160
  monthly_cost: $84.16

storage:
  s3_standard:
    purpose: Model artifacts, backups
    size_gb: 50
    pricing: $0.023/GB/month
    monthly_cost: $1.15

  ebs_gp3:
    purpose: Instance storage
    size_gb: 100
    pricing: $0.08/GB/month
    monthly_cost: $8.00

database:
  service: AWS RDS PostgreSQL
  instance: db.t3.micro
  specs:
    - 2 vCPUs
    - 1 GB RAM
    - 20 GB storage
  pricing: $0.017/hour
  monthly_cost: $12.41

networking:
  data_transfer_out: 10 GB/month
  pricing: $0.09/GB (first 10TB)
  monthly_cost: $0.90

monitoring:
  cloudwatch_basic: Included
  monthly_cost: $0

total_development: $106.62/month
Development Cost Breakdown:

Compute: $84.16 (79%)
Database: $12.41 (12%)
Storage: $9.15 (9%)
Network: $0.90 (<1%)
🏗️ Staging Environment Costs
Pre-Production Testing Environment
YAML

compute:
  service: AWS EKS (Kubernetes)
  node_group:
    instance_type: g4dn.xlarge
    min_nodes: 1
    max_nodes: 3
    avg_nodes: 2
  pricing:
    eks_control_plane: $0.10/hour ($73/month)
    worker_nodes: 2 x $0.526/hour x 730 hours = $767.96/month
  monthly_cost: $840.96

storage:
  s3_intelligent_tiering:
    size_gb: 100
    pricing: $0.0125/GB (frequently accessed)
    monthly_cost: $1.25

  ebs_volumes:
    per_node: 100 GB
    nodes: 2
    total_gb: 200
    pricing: $0.08/GB/month
    monthly_cost: $16.00

database:
  service: AWS RDS PostgreSQL
  instance: db.t3.small
  specs:
    - 2 vCPUs
    - 2 GB RAM
    - 50 GB storage
  pricing: $0.034/hour
  monthly_cost: $24.82

load_balancer:
  service: AWS Application Load Balancer
  pricing:
    alb_hour: $0.0225/hour ($16.43/month)
    lcu_hour: ~$0.50/hour ($365/month estimated)
  monthly_cost: $16.43

networking:
  data_transfer: ~50 GB/month
  nat_gateway: $0.045/hour ($32.85/month)
  monthly_cost: $37.35

monitoring:
  cloudwatch_detailed: ~$10/month
  prometheus: Self-hosted (included in compute)
  monthly_cost: $10

total_staging: $946.81/month
Staging Cost Breakdown:

Compute (EKS): $840.96 (89%)
Database: $24.82 (3%)
Networking: $37.35 (4%)
Storage: $17.25 (2%)
Monitoring: $10 (1%)
Load Balancer: $16.43 (2%)
🌟 Production Environment Costs
Full Production Deployment (High Availability)
YAML

compute:
  service: AWS EKS
  node_groups:
    gpu_nodes:
      instance_type: g4dn.xlarge
      count: 4
      pricing: 4 x $0.526/hour x 730 = $1,535.92

    cpu_nodes:
      instance_type: c5.xlarge
      count: 2
      pricing: 2 x $0.17/hour x 730 = $248.20

  eks_control_plane: $73/month

  monthly_cost: $1,857.12

storage:
  s3_multi_region:
    primary_region: 200 GB
    replica_region: 200 GB
    total: 400 GB
    pricing: $0.023/GB/month
    cross_region_transfer: ~$18/month
    monthly_cost: $27.20

  ebs_volumes:
    gpu_nodes: 4 x 100 GB
    cpu_nodes: 2 x 50 GB
    total: 500 GB
    pricing: $0.08/GB/month
    monthly_cost: $40.00

  ebs_snapshots:
    size: 200 GB
    pricing: $0.05/GB/month
    monthly_cost: $10.00

database:
  service: AWS RDS PostgreSQL
  instance: db.r5.large (HA with Multi-AZ)
  specs:
    - 2 vCPUs
    - 16 GB RAM
    - 100 GB storage (SSD)
    - Multi-AZ deployment
  pricing: $0.24/hour x 730 = $175.20
  backup_storage: 50 GB x $0.095 = $4.75
  monthly_cost: $179.95

cache:
  service: AWS ElastiCache Redis
  instance: cache.t3.medium
  specs:
    - 2 vCPUs
    - 3.09 GB RAM
  pricing: $0.068/hour
  monthly_cost: $49.64

load_balancer:
  service: AWS Application Load Balancer
  zones: 2
  pricing:
    alb_hour: $0.0225/hour x 730 = $16.43
    lcu_processing: ~$30/month
  monthly_cost: $46.43

networking:
  data_transfer_out: 500 GB/month
  pricing:
    first_10tb: $0.09/GB
  nat_gateway: 2 x $0.045/hour x 730 = $65.70
  route53: $0.50/hosted zone = $0.50
  monthly_cost: $111.20

monitoring:
  cloudwatch:
    metrics: ~$10/month
    logs: ~$15/month
  prometheus_grafana:
    storage: ~$5/month
  monthly_cost: $30

backup_disaster_recovery:
  cross_region_snapshots: $20/month
  s3_glacier_deep_archive: $10/month
  monthly_cost: $30

security:
  aws_secrets_manager: $0.40/secret x 10 = $4
  aws_waf: $5/month
  monthly_cost: $9

total_production: $2,350.54/month
Production Cost Breakdown:

Compute (EKS + EC2): $1,857.12 (79%)
Database: $179.95 (8%)
Networking: $111.20 (5%)
Storage: $77.20 (3%)
Cache: $49.64 (2%)
Load Balancer: $46.43 (2%)
Monitoring: $30 (1%)
Backup/DR: $30 (1%)
Security: $9 (<1%)
🚀 High Availability / Enterprise Costs
Multi-Region, 99.99% Uptime SLA
YAML

compute:
  primary_region:
    gpu_nodes: 6 x g4dn.xlarge = $2,303.88
    cpu_nodes: 4 x c5.xlarge = $496.40

  secondary_region:
    gpu_nodes: 4 x g4dn.xlarge = $1,535.92
    cpu_nodes: 2 x c5.xlarge = $248.20

  eks_control_plane: 2 x $73 = $146

  monthly_cost: $4,730.40

database:
  service: AWS Aurora Global Database
  instance: db.r5.2xlarge (primary + replica)
  regions: 2
  pricing: 2 x $0.48/hour x 730 = $700.80
  storage: 500 GB x $0.10/GB = $50
  monthly_cost: $750.80

global_accelerator:
  service: AWS Global Accelerator
  pricing:
    fixed: $0.025/hour = $18.25
    dpu_processing: ~$50/month
  monthly_cost: $68.25

cdn:
  service: AWS CloudFront
  data_transfer: 2 TB
  requests: 10M
  pricing:
    data_transfer: $170
    requests: $10
  monthly_cost: $180

total_high_availability: $5,729.45/month
📊 External Service Costs (All Tiers)
YAML

openrouter_gemini:
  model: Gemini 2.0 Flash
  pricing:
    input: $0.075 per 1M tokens
    output: $0.30 per 1M tokens

  usage_estimates:
    development: 10K requests/month
      input_tokens: 5M
      output_tokens: 2M
      cost: $0.375 + $0.60 = $0.98

    staging: 50K requests/month
      input_tokens: 25M
      output_tokens: 10M
      cost: $1.875 + $3.00 = $4.88

    production: 200K requests/month
      input_tokens: 100M
      output_tokens: 40M
      cost: $7.50 + $12.00 = $19.50

    enterprise: 1M requests/month
      input_tokens: 500M
      output_tokens: 200M
      cost: $37.50 + $60.00 = $97.50

edge_tts:
  provider: Microsoft Edge TTS
  pricing: Free (with rate limits)
  rate_limit: ~1000 requests/day
  overage_plan: N/A (use Azure TTS if needed)

  azure_tts_fallback:
    pricing: $15 per 1M characters
    estimated_usage: 500K chars/month
    cost: $7.50

stack_auth:
  plan: Developer
  pricing: Free up to 5000 MAU
  monthly_cost: $0

  upgrade_threshold: >5000 MAU
  paid_plan: $99/month + $0.05/MAU over 5000

monitoring_services:
  sentry_error_tracking:
    plan: Team
    monthly_cost: $26

  datadog_apm: (optional)
    plan: Pro
    monthly_cost: $31/host x 6 hosts = $186
💡 Cost Optimization Strategies
1. Compute Savings
YAML

reserved_instances:
  commitment: 1 year, all upfront
  g4dn_xlarge_savings: 40%
  original: $0.526/hour
  reserved: $0.316/hour
  annual_savings_per_instance: ~$1,837

spot_instances:
  use_case: Training jobs, non-critical processing
  g4dn_xlarge_spot: ~$0.16/hour (70% savings)
  risk: Can be interrupted
  recommendation: Use for TFX pipeline training only

auto_scaling:
  scale_down_after_hours: 18:00-08:00 (50% capacity)
  weekend_scale: Minimum replicas only
  estimated_savings: 30% on compute

savings_summary:
  reserved_instances: $7,348/year (4 GPU nodes)
  spot_for_training: $200/month
  auto_scaling: $400/month
  total_monthly_savings: ~$1,212
2. Storage Savings
YAML

intelligent_tiering:
  s3_auto_tiering: Saves 30-40% on infrequently accessed data
  monthly_savings: ~$50

lifecycle_policies:
  move_to_glacier_after: 90 days
  delete_old_logs_after: 180 days
  monthly_savings: ~$30
3. Data Transfer Savings
YAML

cloudfront_caching:
  cache_hit_ratio: 80%
  data_transfer_savings: $60/month

vpc_endpoints:
  avoid_nat_gateway: Save $32.85/month per AZ
  s3_endpoint: Free data transfer within region
📈 Cost Scaling Projections
Monthly Costs by Stage
Metric	Development	Staging	Production	Enterprise
Users/Month	10	100	1,000	10,000
Predictions/Month	500	5,000	50,000	500,000
Compute	$84	$841	$1,857	$4,730
Database	$12	$25	$180	$751
Storage	$9	$17	$77	$200
Network	$1	$37	$111	$300
External APIs	$1	$5	$20	$98
Other	$0	$22	$106	$195
TOTAL/Month	$107	$947	$2,351	$6,274
TOTAL/Year	$1,284	$11,364	$28,212	$75,288
Cost Per Prediction
Tier	Cost/Prediction	Includes
Development	$0.21	Infrastructure + APIs
Staging	$0.19	Infrastructure + APIs
Production	$0.047	Infrastructure + APIs + HA
Enterprise	$0.0125	Infrastructure + APIs + Multi-region
🎯 Budget Recommendations
Phase 0-1 (Days 1-7): Development Only
YAML

recommended_budget: $150/month
allocation:
  aws_development: $107
  openrouter_api: $10
  testing_services: $20
  buffer: $13
Phase 2-6 (Days 7-22): Staging Added
YAML

recommended_budget: $1,100/month
allocation:
  aws_development: $107
  aws_staging: $947
  openrouter_api: $20
  monitoring: $26
Phase 7+ (Days 22+): Production Ready
YAML

recommended_budget: $2,600/month
allocation:
  aws_production: $2,351
  openrouter_api: $20
  monitoring_apm: $186
  cdn: $30
  buffer: $13
💳 Payment & Billing Setup
AWS Setup
Bash

# Set up billing alerts
aws cloudwatch put-metric-alarm \
  --alarm-name "BillingAlert-500USD" \
  --alarm-description "Alert when AWS bill exceeds $500" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 500 \
  --comparison-operator GreaterThanThreshold

# Set up budget
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json
budget.json:

JSON

{
  "BudgetName": "VoxRayAI-Production-Budget",
  "BudgetLimit": {
    "Amount": "3000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
📊 Cost Monitoring Dashboard
Track these metrics daily:

YAML

key_metrics:
  - total_daily_spend
  - compute_hours_used
  - gpu_utilization_percent
  - api_requests_count
  - data_transfer_gb
  - storage_gb_used

alerts:
  - daily_spend > $100
  - monthly_projected > $3000
  - gpu_utilization < 40% (underutilized)
  - api_cost_per_request > $0.05
🔄 Cost Review Schedule
YAML

daily:
  - Check AWS Cost Explorer
  - Verify no runaway resources

weekly:
  - Review top 10 cost drivers
  - Check reserved instance utilization
  - Review auto-scaling effectiveness

monthly:
  - Full cost breakdown analysis
  - Compare actual vs. budget
  - Optimize based on usage patterns
  - Update projections
Last Updated: 2025-01-31
Maintained By: AG-05 (DevOpsArchitect), Human Coordinator
Review Frequency: Weekly during development, Monthly in production

text


---

```
