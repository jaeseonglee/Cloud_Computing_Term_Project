import boto3
from PIL import Image

#사진에서 마스크를 탐지하는 함수, BoundingBoxs를 리턴
def detect_masks(photo, bucket):
    client=boto3.client('rekognition')
    BoundingBoxs = []   #사진에서 마스크를 쓰지 않은 사람들의 위치값들

    #AWS에 마스크 탐지 요청
    response = client.detect_protective_equipment(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, SummarizationAttributes={'MinConfidence':80, 'RequiredEquipmentTypes':['FACE_COVER']})

    for i in range(len(response['Persons'])):
        if(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"] == []):    #마스크 탐지 안됨
            BoundingBoxs.append(response['Persons'][i]['BoundingBox'])
        elif(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False): #마스크를 제대로 착용하지 않음
            BoundingBoxs.append(response['Persons'][i]['BoundingBox'])

    return BoundingBoxs


#사진을 분할하는 함수
def file_split(image_file, BoundingBoxs):
    image = Image.open(image_file)
    
    bucket = 'cc--result'   #마스크를 안쓴사람들을 모은 버킷

    num = 1
    for BoundingBox in BoundingBoxs:

        #위치값이 음수인 경우 0으로 변환
        if BoundingBox['Width'] < 0 :
            BoundingBox['Width'] = 0
        if BoundingBox['Height'] < 0 :
            BoundingBox['Height'] = 0
        if BoundingBox['Left'] < 0 :
            BoundingBox['Left'] = 0
        if BoundingBox['Top'] < 0 :
            BoundingBox['Top'] = 0

        #AWS에서 받아온 사람위치 데이터(비율)을 픽셀단위로 변환
        size = image.size

        x1 = size[0] * BoundingBox['Left']
        y1 = size[1] * BoundingBox['Top']
        x2 = x1 + size[0] * BoundingBox['Width']
        y2 = y1 + size[1] * BoundingBox['Height']

        #사진분할
        croppedImage = image.crop((x1,y1,x2,y2))

        #사진 저장
        image_file_name = image_file[:-4] + "_Det" +str(num) + ".jpg"
        croppedImage.save(image_file_name)

        file_upload(bucket, image_file_name)

        num += 1

          
#파일을 버킷에 업로드하는 함수
def file_upload(bucket, upload_file):
    s3 = boto3.client('s3')
    return s3.upload_file(upload_file, bucket, upload_file)

    
def main():
    bucket = 'cc--image' # 원본 이미지 버킷
    
    while True:
        try:
            image_file = input("사진 파일 이름 입력(확장자명 포함) (종료: q)): ")
            
            if(image_file == 'q'):
                print("종료합니다")
                break
            
            #확장자가 .jpg 와 .png가 아닌경우 다시 입력 받음
            if((image_file[-4:] != ".jpg") & (image_file[-4:] != ".png") ):
                print("확장자명 오류")
                print(".jpg .png 파일만 가능합니다. ")
                continue

            #버킷에 중복된 파일명이 있는지 검사
            close = False
            s3 = boto3.client('s3')
            response = s3.list_objects(Bucket = bucket)
            for i in response['Contents']:
                if(image_file == i['Key']):
                    menu = int(input("버킷에 동일한 이름의 파일이 존재합니다.\n1.덮어쓰기 2.처음으로 돌아가기 : "))
                    if(menu == 1):
                        break
                    elif(menu == 2):
                        close = True
                        break
            if(close):
                continue

            #S3 서비스를 이용하여 이미지를 버킷(cc-image)에 저장
            file_upload(bucket, image_file)

            #마스크 탐지
            BoundingBoxs = detect_masks(image_file, bucket)

            if(len(BoundingBoxs) == 0):
                print("마스크를 모두 잘 착용중")
            else:
                print("마스크를 착용하지 않은 사람", len(BoundingBoxs), "명 발견")
                print("사진을 분할하여 저장합니다")
                file_split(image_file, BoundingBoxs)
        except IOError:
            print(image_file + "을 찾지 못했습니다.")
        except:
            print("에러발생")

if __name__ == "__main__":
    main()
