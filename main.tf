# Terraform configuration for Autonomous JARVIS deployment
# Конфигурация Terraform для развертывания автономной системы JARVIS

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "AWS Key Pair name"
  type        = string
}

# VPC
resource "aws_vpc" "jarvis_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "jarvis-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "jarvis_igw" {
  vpc_id = aws_vpc.jarvis_vpc.id

  tags = {
    Name = "jarvis-igw"
  }
}

# Subnet
resource "aws_subnet" "jarvis_subnet" {
  vpc_id                  = aws_vpc.jarvis_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "jarvis-subnet"
  }
}

# Route Table
resource "aws_route_table" "jarvis_rt" {
  vpc_id = aws_vpc.jarvis_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.jarvis_igw.id
  }

  tags = {
    Name = "jarvis-rt"
  }
}

resource "aws_route_table_association" "jarvis_rta" {
  subnet_id      = aws_subnet.jarvis_subnet.id
  route_table_id = aws_route_table.jarvis_rt.id
}

# Security Group
resource "aws_security_group" "jarvis_sg" {
  name_prefix = "jarvis-sg"
  vpc_id      = aws_vpc.jarvis_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jarvis-sg"
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 Instance
resource "aws_instance" "jarvis" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name              = var.key_name
  vpc_security_group_ids = [aws_security_group.jarvis_sg.id]
  subnet_id             = aws_subnet.jarvis_subnet.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    domain = aws_eip.jarvis_eip.public_ip
  }))

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

  tags = {
    Name = "autonomous-jarvis"
  }
}

# Elastic IP
resource "aws_eip" "jarvis_eip" {
  domain = "vpc"
  
  tags = {
    Name = "jarvis-eip"
  }
}

resource "aws_eip_association" "jarvis_eip_assoc" {
  instance_id   = aws_instance.jarvis.id
  allocation_id = aws_eip.jarvis_eip.id
}

# Output
output "jarvis_public_ip" {
  description = "Public IP address of the JARVIS instance"
  value       = aws_eip.jarvis_eip.public_ip
}

output "jarvis_web_url" {
  description = "Web URL for JARVIS"
  value       = "https://${aws_eip.jarvis_eip.public_ip}"
}
