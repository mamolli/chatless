provider "aws" {
  region = "us-east-1"
}

resource "aws_lambda_function" "lambda_function" {
  role             = "${aws_iam_role.lambda_exec_role.arn}"
  handler          = "chatbot.handle"
  runtime          = "python3.7"
  filename         = "chatbot.zip"
  function_name    = "pychat"
}

resource "aws_iam_role" "lambda_exec_role" {
  name        = "lambda_exec"
  path        = "/"
  description = ""

  assume_role_policy = "${file("lambda_policy.json")}"
}

resource "aws_iam_policy" "lambda_logging" {
  name = "lambda_logging"
  path = "/"
  description = "IAM policy for logging from a lambda"

  policy = "${file("lambda_cloudwatch_policy.json")}" 
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role = "${aws_iam_role.lambda_exec_role.name}"
  policy_arn = "${aws_iam_policy.lambda_logging.arn}"
}

resource "aws_api_gateway_rest_api" "lambda_chatbot" {
  name        = "lambda_chatbot"
  description = ""
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  parent_id   = "${aws_api_gateway_rest_api.lambda_chatbot.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda_function.invoke_arn}"
}
resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  resource_id   = "${aws_api_gateway_rest_api.lambda_chatbot.root_resource_id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  resource_id = "${aws_api_gateway_method.proxy_root.resource_id}"
  http_method = "${aws_api_gateway_method.proxy_root.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda_function.invoke_arn}"
}

resource "aws_api_gateway_deployment" "lambda" {
  depends_on = [
    "aws_api_gateway_integration.lambda",
    "aws_api_gateway_integration.lambda_root",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.lambda_chatbot.id}"
  stage_name  = "test"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_function.arn}"
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_deployment.lambda.execution_arn}/*/*"
}

output "base_url" {
  value = "${aws_api_gateway_deployment.lambda.invoke_url}"
}