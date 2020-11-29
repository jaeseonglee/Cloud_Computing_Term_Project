import boto3
from PIL import Image

#사진에서 마스크를 탐지하는 함수, BoundingBoxs를 리턴
def detect_masks(photo, bucket):
    client=boto3.client('rekognition')
    BoundingBoxs = []   #사진에서 마스크를 쓰지 않은 사람들의 위치값

    response = client.detect_protective_equipment(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, 
        SummarizationAttributes={'MinConfidence':80, 'RequiredEquipmentTypes':['FACE_COVER']})

    for i in range(len(response['Persons'])):
        if(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"] == []):    #마스크 탐지 안됨
            BoundingBoxs.append(response['Persons'][i]['BoundingBox'])
        elif(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False): #마스크를 제대로 착용하지 않음
            BoundingBoxs.append(response['Persons'][i]['BoundingBox'])

    return BoundingBoxs


#사진을 분할하는 함수
def file_split(image_file, BoundingBoxs):
    print("file_split 함수 실행")
    
    image = Image.open(image_file)
    
    bucket = 'cc--result'   #마스크를 안쓴사람들을 모은 버킷

    num = 1
    for BoundingBox in BoundingBoxs:
        if BoundingBox['Width'] < 0 :
            BoundingBox['Width'] = 0
        if BoundingBox['Height'] < 0 :
            BoundingBox['Height'] = 0
        if BoundingBox['Left'] < 0 :
            BoundingBox['Left'] = 0
        if BoundingBox['Top'] < 0 :
            BoundingBox['Top'] = 0

        size = image.size

        x1 = size[0] * BoundingBox['Left']
        y1 = size[1] * BoundingBox['Top']
        x2 = x1 + size[0] * BoundingBox['Width']
        y2 = y1 + size[1] * BoundingBox['Height']

        croppedImage = image.crop((x1,y1,x2,y2))

        image_file_name = image_file[:-4] + "_Det" +str(num) + ".jpg"
        croppedImage.save(image_file_name) #파일명

        file_upload(bucket, image_file_name)
        
        num += 1

          
#파일을 버킷에 업로드하는 함수
def file_upload(bucket, upload_file):
    s3 = boto3.client('s3')

    return s3.upload_file(upload_file, bucket, upload_file)

    #매개변수    
    #로컬에서 올릴 파일이름
    #S3 버킷 이름
    #버킷에 저장될 파일 이름 (로컬의 파일명과 동일) 버킷에 이미 있는 파일명이면 덮어쓰기

    
def main():
    bucket = 'cc--image' # rekognition에 사용하기 전 이미지 버킷

    while True:
        image_file = input("사진 파일 이름 입력(종료: q)): ")
        
        if(image_file == 'q'):
            print("종료합니다")
            break
        
        file_upload(bucket, image_file)   #S3 서비스를 이용하여 a를 버킷(cc-image)에 저장
        BoundingBoxs = detect_masks(image_file, bucket)    #마스크 탐지

        if(len(BoundingBoxs) == 0):
            print("마스크를 모두 잘 착용중")
        else:
            print("마스크를 착용하지 않은 사람", len(BoundingBoxs), "명 발견")
            print("사진을 분할하여 저장합니다")
            file_split(image_file, BoundingBoxs)


if __name__ == "__main__":
    main()
