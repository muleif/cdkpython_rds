from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy as remove,
    # aws_sqs as sqs,
)

# import aws_cdk
from constructs import Construct
from aws_cdk import CfnOutput
class RdsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Prod_configs = self.node.try_get_context("envs")["Prod"]

        #  Create a custome VPC
        custom_vpc = ec2.Vpc(
            self, "customvpc",
            ip_addresses= ec2.IpAddresses.cidr(Prod_configs['vpc_config']['vpc_cidr']),
            max_azs= 2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet", cidr_mask=Prod_configs["vpc_config"]["cidr_mask"], subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet", cidr_mask=Prod_configs["vpc_config"]["cidr_mask"], subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ])
        
        #Create an RDS Database
        myDB = rds.DatabaseInstance(self, 
                                    "MyDatabase",
                                    engine= rds.DatabaseInstanceEngine.MYSQL,
                                    vpc= custom_vpc,
                                    vpc_subnets= ec2.SubnetSelection(
                                        subnet_type= ec2.SubnetType.PUBLIC,
                                    ),
                                    credentials= rds.Credentials.from_generated_secret("Admin"),
                                    instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                                       ec2.InstanceSize.MICRO),
                                    port= 3306,
                                    allocated_storage= 80,
                                    multi_az= False,
                                    removal_policy= remove.DESTROY,
                                    deletion_protection= False,
                                    publicly_accessible= True
                                    )
        
        myDB.connections.allow_from_any_ipv4(
            ec2.Port.tcp(3306),
            description= "Open port for connection"
        )

        
        CfnOutput(self, 
                  "db_endpoint",
                  value= myDB.db_instance_endpoint_address)
        
        
