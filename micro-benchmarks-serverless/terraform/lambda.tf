locals {
  python_source_file = "../python/lambda_function.py"
  python_otel_layer  = "arn:aws:lambda:${local.region}:184161586896:layer:opentelemetry-python-0_5_0:1"
}

module "python_json" {
  source = "./modules/lambda-function"

  name             = "${local.name}-python-json"
  iam_role_arn     = aws_iam_role.lambda_execution_role.arn
  lambda_handler   = "lambda_function.lambda_handler"
  lambda_runtime   = "python3.9"
  source_file      = "../python/${local.python_source_file}"
  api_gw_path_part = "json"
  parent_id        = aws_api_gateway_resource.python.id
  rest_api_id      = aws_api_gateway_rest_api.api.id
}

module "python_json_otel" {
  source = "./modules/lambda-function"

  name             = "${local.name}-python-json-otel"
  iam_role_arn     = aws_iam_role.lambda_execution_role.arn
  lambda_handler   = "lambda_function.lambda_handler"
  lambda_runtime   = "python3.9"
  source_file      = local.python_source_file
  api_gw_path_part = "json-otel"
  parent_id        = aws_api_gateway_resource.python.id
  rest_api_id      = aws_api_gateway_rest_api.api.id
  layers           = [local.python_otel_layer]
  env_variables = {
    OTEL_TRACES_EXPORTER = "console"
    OTEL_METRICS_EXPORTER = "console"
    OTEL_SERVICE_NAME = "python-json-otel"
    AWS_LAMBDA_EXEC_WRAPPER= "/opt/otel-instrument"
  }
}
