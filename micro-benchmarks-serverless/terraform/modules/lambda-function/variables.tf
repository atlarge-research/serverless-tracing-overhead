variable "name" {
  type        = string
  description = "Name of the lambda function"
}

variable "iam_role_arn" {
  type        = string
  description = "ARN of the IAM role to attach to the Lambda function"
}

variable "source_file" {
  type        = string
  description = "Name of the source file(s) to pack"
}

variable "lambda_handler" {
  type        = string
  description = "Lambda handler"
}

variable "lambda_runtime" {
  type        = string
  description = "Lambda runtime"
}

variable "rest_api_id" {
  type        = string
  description = "REST API Gateway id"
}

variable "api_gw_path_part" {
  type        = string
  description = "API Gateway path part"
}

variable "parent_id" {
  type        = string
  description = "API Gateway resource parent ID"
}

variable "layers" {
  type = list(string)
  description = "List of Lambda layers"
  default = []
}