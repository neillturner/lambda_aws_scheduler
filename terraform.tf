terraform {
  backend "s3" {
    bucket = "my-devops-state"
    key    = "dev/aws_scheduler/terraform.state"
    region = "eu-west-1"
    encrypt = "true" 
  }
}
