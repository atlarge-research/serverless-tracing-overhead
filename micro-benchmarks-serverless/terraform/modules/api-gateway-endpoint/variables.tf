variable "rest_api_id" {
  type        = string
  description = "ID of the Rest API"
}

variable "lambda_invoke_arn" {
  type        = string
  description = "Invoke ARN of the AWS Lambda function"
}

variable "path_part" {
  type        = string
  description = "Name of the API path"
}

variable "api_key_required" {
  type        = bool
  description = "Specify if the method requires an API key"
  default     = true
}

variable "parent_id" {
  type        = string
  description = "Parent id of the API resource"
}