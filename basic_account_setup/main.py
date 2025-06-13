import pulumi
import pulumi_aws as aws

# Load configuration
config = pulumi.Config()
region = config.require("region")
environment = config.get("environment") or "dev"
vpc_cidr = config.require("vpc_cidr")
public_subnet_cidr = config.require("public_subnet_cidr")
private_subnet_cidr = config.require("private_subnet_cidr")
public_subnet_az = config.require("public_subnet_az")
private_subnet_az = config.require("private_subnet_az")
ami_id = config.require("ami_id")
instance_type = config.require("instance_type")
instance_count = config.require_int("instance_count")
backup_schedule = config.require("backup_schedule")
backup_retention_days = config.require_int("backup_retention_days")

# Create VPC
vpc = aws.ec2.Vpc(f"{environment}-vpc",
    cidr_block=vpc_cidr,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": f"{environment}-vpc"}
)

# Create Subnets
public_subnet = aws.ec2.Subnet(f"{environment}-public-subnet",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidr,
    map_public_ip_on_launch=True,
    availability_zone=public_subnet_az,
    tags={"Name": f"{environment}-public-subnet"}
)

private_subnet = aws.ec2.Subnet(f"{environment}-private-subnet",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidr,
    availability_zone=private_subnet_az,
    tags={"Name": f"{environment}-private-subnet"}
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway(f"{environment}-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{environment}-igw"}
)

# Create Route Table
public_rt = aws.ec2.RouteTable(f"{environment}-public-rt",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id
    }],
    tags={"Name": f"{environment}-public-route-table"}
)

# Route Table Association
aws.ec2.RouteTableAssociation(f"{environment}-public-rt-assoc",
    subnet_id=public_subnet.id,
    route_table_id=public_rt.id
)

# Security Group for EC2 and ALB
sg = aws.ec2.SecurityGroup(f"{environment}-app-sg",
    vpc_id=vpc.id,
    ingress=[
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]}
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}],
    tags={"Name": f"{environment}-app-security-group"}
)

# Create Application Load Balancer
alb = aws.lb.LoadBalancer(f"{environment}-app-alb",
    subnets=[public_subnet.id],
    security_groups=[sg.id],
    load_balancer_type="application",
    tags={"Name": f"{environment}-app-alb"}
)

# Target Group for ALB
tg = aws.lb.TargetGroup(f"{environment}-app-tg",
    port=80,
    protocol="HTTP",
    vpc_id=vpc.id,
    target_type="instance",
    health_check={
        "path": "/",
        "protocol": "HTTP"
    },
    tags={"Name": f"{environment}-app-target-group"}
)

# Listener for ALB
aws.lb.Listener(f"{environment}-app-listener",
    load_balancer_arn=alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[{
        "type": "forward",
        "target_group_arn": tg.arn
    }]
)

# EC2 Instances
instances = []
for i in range(instance_count):
    instance = aws.ec2.Instance(f"{environment}-web-instance-{i+1}",
        ami=ami_id,
        instance_type=instance_type,
        subnet_id=public_subnet.id,
        security_groups=[sg.name],
        tags={"Name": f"{environment}-web-instance-{i+1}"}
    )
    instances.append(instance)
    # Register instance with Target Group
    aws.lb.TargetGroupAttachment(f"{environment}-tg-attachment-{i+1}",
        target_group_arn=tg.arn,
        target_id=instance.id
    )

# AWS Backup Vault
backup_vault = aws.backup.Vault(f"{environment}-backup-vault",
    tags={"Name": f"{environment}-backup-vault"}
)

# AWS Backup Plan
backup_plan = aws.backup.Plan(f"{environment}-backup-plan",
    rules=[{
        "rule_name": "daily-backup",
        "target_vault_name": backup_vault.name,
        "schedule": backup_schedule,
        "lifecycle": {
            "delete_after": backup_retention_days
        }
    }],
    tags={"Name": f"{environment}-backup-plan"}
)

# AWS Backup Selection
aws.backup.Selection(f"{environment}-backup-selection",
    plan_id=backup_plan.id,
    resources=[instance.arn for instance in instances],
    selection_name=f"{environment}-ec2-backup-selection"
)

# Export outputs
pulumi.export("vpc_id", vpc.id)
pulumi.export("alb_dns", alb.dns_name)