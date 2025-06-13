# Pulumi AWS Infrastructure
This repository uses Pulumi with Python to provision an AWS infrastructure, including a VPC, subnets, route tables, an application load balancer, EC2 instances, and AWS Backup for instance backups. Dependencies are managed using Poetry, and configuration is handled via Pulumi stack configuration files.
Prerequisites

## Pulumi CLI installed
Python 3.8+ and Poetry installed (pip install poetry)
AWS CLI configured with appropriate credentials
Permissions to create VPCs, subnets, route tables, load balancers, EC2 instances, and AWS Backup resources

## Resources Created

**VPC:** Configurable CIDR block
**Subnets:** One public and one private subnet with configurable CIDR blocks and availability zones
**Internet Gateway:** Attached to the VPC
**Route Table:** Public route table with internet access
**Security Group:** Allows HTTP (port 80) and SSH (port 22) ingress
**Application Load Balancer:** Forwards traffic to EC2 instances
**EC2 Instances:** Configurable number of instances with specified AMI and instance type
**AWS Backup:** Daily backups for EC2 instances with configurable schedule and retention period

## Configuration

Configuration values (e.g., CIDR blocks, region, AMI ID) are defined in Pulumi.<stack-name>.yaml (e.g., Pulumi.dev.yaml).
Sample configuration:config:
 ``` aws:region: us-east-1
  pulumi-resources:region: us-east-1
  pulumi-resources:environment: dev
  pulumi-resources:vpc_cidr: 10.1.0.0/16
  pulumi-resources:public_subnet_cidr: 10.1.1.0/24
  pulumi-resources:private_subnet_cidr: 10.1.2.0/24
  pulumi-resources:public_subnet_az: us-east-1a
  pulumi-resources:private_subnet_az: us-east-1b
  pulumi-resources:ami_id: ami-0e86e20dae9224db8 # Change to your desire AMI
  pulumi-resources:instance_type: t2.micro
  pulumi-resources:instance_count: 2
  pulumi-resources:backup_schedule: cron(0 5 * * ? *)
  pulumi-resources:backup_retention_days: 30 ```


Create or modify Pulumi.dev.yaml in the project root to customize values.

## Usage

Clone the repository:git clone <repository-url>
cd pulumi-aws-infrastructure


Install dependencies using Poetry: `poetry install`


Activate the Poetry virtual environment: `poetry shell`


Initialize Pulumi stack: `pulumi stack init dev`


Set configuration values (if not using a Pulumi.dev.yaml file):pulumi config set aws:region us-east-1
pulumi config set pulumi-resources:region us-east-1
pulumi config set pulumi-resources:vpc_cidr 10.1.0.0/16
Set other configs as needed


Deploy the infrastructure: `pulumi up`


View outputs (e.g., ALB DNS name):pulumi stack output


Destroy resources: `pulumi destroy`



Notes

Ensure the AMI ID matches the target region and is valid for Amazon Linux 2 or your desired OS.
Ensure AWS credentials are configured via environment variables or AWS CLI.
This setup is for demonstration; production environments may need additional configurations like high availability or enhanced security.

