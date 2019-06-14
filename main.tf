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
  description = "Allows Lambda Function to call AWS services on your behalf."

  assume_role_policy = "${file("lambda_policy.json")}"
}