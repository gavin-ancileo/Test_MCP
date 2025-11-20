#!/usr/bin/env python3
"""Create n8n service registry and update ECS service"""
import boto3
import sys

region = 'ap-southeast-2'
cluster = 'aap-cluster'
service = 'aap-cluster-n8n'

ecs = boto3.client('ecs', region_name=region)
sd = boto3.client('servicediscovery', region_name=region)

print("Finding namespace...")
ns_list = sd.list_namespaces(MaxResults=5)['Namespaces']
aap_ns_id = None
for ns in ns_list:
    if 'aap.local' in ns.get('Name', ''):
        aap_ns_id = ns['Id']
        print(f"Found namespace: {ns['Name']} ({aap_ns_id})")
        break

if not aap_ns_id:
    print("ERROR: No aap.local namespace")
    sys.exit(1)

print("\nFinding or creating service registry 'aap-n8n'...")
try:
    # Check if it already exists
    services = sd.list_services(
        Filters=[{'Name': 'NAMESPACE_ID', 'Values': [aap_ns_id]}],
        MaxResults=10
    )['Services']
    
    registry_arn = None
    for svc in services:
        if svc['Name'] == 'aap-n8n':
            registry_arn = svc['Arn']
            print(f"✅ Found existing registry: {registry_arn}")
            break
    
    if not registry_arn:
        # Create new one
        response = sd.create_service(
            Name='aap-n8n',
            NamespaceId=aap_ns_id,
            DnsConfig={
                'NamespaceId': aap_ns_id,
                'DnsRecords': [{'Type': 'A', 'TTL': 60}],
                'RoutingPolicy': 'MULTIVALUE'
            },
            HealthCheckCustomConfig={
                'FailureThreshold': 1
            }
        )
        registry_arn = response['Service']['Arn']
        print(f"✅ Created new service registry: {registry_arn}")
    
    print(f"\nUpdating ECS service {service}...")
    result = ecs.update_service(
        cluster=cluster,
        service=service,
        serviceRegistries=[{'registryArn': registry_arn}],
        forceNewDeployment=True
    )
    
    print("✅ SUCCESS! Service registry created and ECS service updated.")
    print(f"Service will restart. DNS should work in 1-2 minutes.")
    print(f"\nRegistry ARN: {registry_arn}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

