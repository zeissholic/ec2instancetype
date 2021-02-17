# ec2instancetype

This python code is for descibing ec2 instance types supported in each availability zones(AZ) and regions in AWS. 

### to run the code: it requires python 3.x and boto3, sys, getopt, json libraries.

Hear are some sample command to run the code

#### to get all instance type in specific region
You can find the region code in https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html 
and avaiable instance type in https://aws.amazon.com/ec2/instance-types/?nc1=h_ls

```
python3 ec2instancetype.py -r ap-northeast-2 -i g4dn.2xlarge -p <AWS profile name>
```
The output shows which AZ has the instance type in the region (ap-northeast-2)
```
[
     {
          "ap-northeast-2": {
               "apne2-az1": [
                    "g4dn.2xlarge"
               ],
               "apne2-az2": "",
               "apne2-az3": [
                    "g4dn.2xlarge"
               ],
               "apne2-az4": ""
          }
     }
]
```