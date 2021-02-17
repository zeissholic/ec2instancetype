import boto3, sys, getopt, json

def main(argv):

    python_file = argv[0] # 파이선 실행 파일명
    regions_arg = "" # 리전명 아규먼트 (,로 구분해서 전달)
    instances_arg = "" # 인스턴스타입 아규먼트 (,로 구분해서 전달)
    profile_name = "" # AWS credential profile
    family_only_yn = ""

    try:
        # opts: getopt 옵션에 따라 파싱 ex) [('-i', 'myinstancce1')]
        # etc_args: getopt 옵션 이외에 입력된 일반 Argument
        # argv 첫번째(index:0)는 파일명, 두번째(index:1)부터 Arguments
        opts, etc_args = getopt.getopt(argv[1:], \
                                 "hr:i:p:f", ["help","region=","chaninstancenel=","profile=","family="])

    except getopt.GetoptError: # 옵션지정이 올바르지 않은 경우
        print(python_file, '-r <region name> -i <instance name> -p <AWS profile name>')
        sys.exit(2)

    for opt, arg in opts: # 옵션이 파싱된 경우
        if opt in ("-h", "--help"): # HELP 요청인 경우 사용법 출력
            print(python_file, '-i <instance name> -c <channel name> -p <AWS profile name>')
            sys.exit()

        elif opt in ("-r", "--region"): # 리전명 입력인 경우
            regions_arg = arg.lower().replace("%","*")

        elif opt in ("-i", "--instance"): # 인스턴스타입 입력인 경우
            instances_arg = arg.lower().replace("%","*")
        
        elif opt in ("-p", "--profile"): # 프로파일 입력인 경우
            profile_name = arg
        
        elif opt in ("-f", "--family"): # 인스턴스패밀리만 보고자 하는 경우
            family_only_yn = True

    if len(regions_arg) < 1: # 필수항목 값이 비어있다면
        print(python_file, "-r or --region option is mandatory") # 필수임을 출력
        sys.exit(2)
    
    if len(instances_arg) < 1: # 필수항목 값이 비어있다면
        print(python_file, "-i or --instance option is mandatory") # 필수임을 출력
        sys.exit(2)
        

    # print("regions_arg:", regions_arg)
    # print("instances_arg:",  instances_arg)


    myregion = regions_arg.split(",")
    insttype = instances_arg.split(",")

    if len(profile_name) > 0:
        boto3.setup_default_session(profile_name=profile_name) # AWS 프로파일을 지정한 경우
    else:
        boto3.setup_default_session() # 디폴트 프로파일 사용

    client = boto3.client('ec2')
    #aws_regions = ec2.describe_regions()

    instancetypeDICT = []
    tempDICT = []
    instanceFamilyDICT = []

    # tempSTR = ""
    i = 0
    r = 0
    a = 0

    #sort_order = ['nano','micro', 'small', 'medium', 'large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge','16xlarge', '20xlarge', '24xlarge', '.metal'] 

    for region in sorted([regions['RegionName'] for regions in client.describe_regions(
        Filters=[{'Name': 'region-name', 'Values': myregion},],
    )['Regions']]): # 리전별
        #region_name = region['RegionName']

        client = boto3.client('ec2', region)
        #print(region)

        instancetypeDICT.insert(r,{region:{}})

        for azid in sorted([azs['ZoneId'] for azs in client.describe_availability_zones(
        Filters=[{'Name': 'region-name', 'Values': [region,]},],
        )['AvailabilityZones']]): # AZ별

            tempDICT.clear()
            instanceFamilyDICT.clear()
            #print('   '+azid)
            for itype in sorted([instancetype['InstanceType'] for instancetype in client.describe_instance_type_offerings(
                LocationType='availability-zone-id',
                Filters=[{'Name': 'location','Values': [azid,]},
                {'Name': 'instance-type','Values': insttype},
                ],
            )['InstanceTypeOfferings']]): # 인스턴스타입별
                #print(region+', '+azid+', '+itype)
                if family_only_yn :
                    instanceFamilyDICT.insert(i, itype.split('.')[0])
                else:
                    tempDICT.insert(i, itype)

                # tempDICT.insert(i, (itype.split('.')[0], itype.split('.')[1]))
                i += 1
            # dedupe
            if family_only_yn :
                for k in range(len(instanceFamilyDICT)): 
                    if instanceFamilyDICT[k] not in instanceFamilyDICT[k + 1:]: 
                        tempDICT.append(instanceFamilyDICT[k]) 

            # sorting the instance type
            # sorted(tempDICT, key=lambda i:sort_order.index(i[0]))
            # print(tempDICT)

            if i > 0:
                instancetypeDICT[r][region][azid]= json.loads(json.dumps(tempDICT))
            else:
                 instancetypeDICT[r][region][azid]= "" 

            i = 0
            a += 1
            #tempSTR = ""

        r += 1    
    
    instancetypeJSON = json.dumps(instancetypeDICT, indent=5)
    
    print(instancetypeJSON)

if __name__ == "__main__":
    main(sys.argv)