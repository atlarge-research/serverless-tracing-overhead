locals {
  zip_output = "${var.name}.zip"
}

variable "env_variables" {
  type = map(string)
  description = "Lambda env variables"
  default = {}
}
resource "aws_lambda_function" "lambda" {
  function_name = var.name

  filename         = local.zip_output
  source_code_hash = data.archive_file.lambda.output_base64sha256
  handler          = var.lambda_handler
  runtime          = var.lambda_runtime

  role = var.iam_role_arn


  layers = var.layers
  environment {
    variables = var.env_variables
  }

  depends_on = [data.archive_file.lambda]
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = var.source_file
  output_path = local.zip_output
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"
}

module "api_gw" {
  source = "../api-gateway-endpoint"

  lambda_invoke_arn = aws_lambda_function.lambda.invoke_arn
  rest_api_id       = var.rest_api_id
  path_part         = var.api_gw_path_part
  parent_id         = var.parent_id
}
