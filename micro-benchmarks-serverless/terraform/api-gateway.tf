locals {
  stage_name = "prod"
}

resource "aws_api_gateway_rest_api" "api" {
  name = "${local.name}-micro-benchmarks"
}

resource "aws_api_gateway_api_key" "micro_benchmarks" {
  name = "micro-benchmarks"
}

resource "aws_api_gateway_usage_plan" "plan" {
  name = "micro-benchmark-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = local.stage_name
  }
}

resource "aws_api_gateway_usage_plan_key" "main" {
  key_id        = aws_api_gateway_api_key.micro_benchmarks.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.plan.id
}


resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = local.stage_name

  triggers = {
    redeployment = timestamp()
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = local.stage_name
}

# /python
resource "aws_api_gateway_resource" "python" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "python"
}