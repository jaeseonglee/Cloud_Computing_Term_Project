## 2020_2_Cloud_Computing_Term_Project
# 프로젝트 명: 마스크 미착용자 검출 프로그램

## 팀 구성원

|학과|학번|이름|담당 파트|
|----------|---------|----------|----------|
|컴퓨터공학과|20165147|유병학|영상처리 프로그래밍|
|빅데이터전공|20165153|이재성|예외 처리 및 오류 수정|
|빅데이터전공|20165164|지현한|AWS 서비스 활용 프로그래밍|
- python 언어를 통해 프로그램을 만들었으며, 팀 구성원끼리 서로 피드백을 하며 진행함.
- 기타 사항
    - 대표학생: 이재성
    - 프로젝트 깃허브 주소: https://github.com/jaeseonglee/Cloud_Computing_Term_Project


## 프로젝트 소개 및 개발 내용 소개
---------
### 프로젝트 소개
- __AWS Rekognition 서비스를 활용하여 사람의 마스크 착용 여부를 확인하고, 착용하지 않은 사람을 저장하는 프로그램입니다.__

 - 저희는 AWS Rekognition 서비스 중 PPE(개인 보호 장비)를 감지하는 서비스를 활용하여 프로그램을 개발했습니다.
    - PPE 감지는 기본적으로 사람을 감지하는 것과 동시에 그 사람이 장갑, 헬멧, 보호 마스크와 같은 보호장비를 감지하는데 사용합니다.

- 저희를 여기서 보호 마스크를 감지하는 것에서 아이디어를 얻었습니다. 아래와 같이 사람들의 일반 마스크 착용 여부도 확인할 수 있다는 것을 알아내고, 이를 활용하여 마스크 인식 프로젝트를 만들게 되었습니다.

![PPE_mask](PPE_mask.png)

 - (원본 사진 출처: 이재성)
 - (위 사진이 사용된 출처: AWS Rekognition PPE 감지 페이지)

### 개발내용 소개

- 개발에 있어 사용한 언어는 python을 통해 만들었으며 3.7 이상의 버전에서 진행했습니다. 

```python
#사용 모듈
import boto3
from PIL import Image
from os.path import getsize
```
- aws 서비스를 사용하기 위한 boto3와 이미지 파일을 다루기 위해 Image를  사용합니다.
- 파일의 크기를 확인하기 위해 os.path 모듈의 getsize를 사용합니다.

```python
detect_protective_equipment(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                SummarizationAttributes={'MinConfidence':80, 'RequiredEquipmentTypes':['FACE_COVER']})

```
- __detect_protective_equipment__ 함수를 통해 Rekognition의 PPE 감지 서비스를 사용합니다. 

- 함수의 반환값 중에는 EquipmentDetections 가 있는데 __FACE_COVER, HAND_COVER, HEAD_COVER__ 중 __FACE_COVER__ 타입 유무를 확인해서 마스크 착용 여부를 판단합니다.

```python
BoundingBoxs = []   #사진에서 마스크를 쓰지 않은 사람들의 위치값들

for i in range(len(response['Persons'])):
        #마스크 탐지 안됨
        if(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"] == []):   
            BoundingBoxs.append(response['Persons'][i]['BoundingBox']) 

        #마스크를 제대로 착용하지 않음
        elif(response['Persons'][i]['BodyParts'][0]["EquipmentDetections"][0]["CoversBodyPart"]["Value"] == False): 
            BoundingBoxs.append(response['Persons'][i]['BoundingBox'])
```
- 함수에서 받은 반환값 중에서 __Persons__ 이 있다면 사람이 감지되었음.

- 사람을 감지한 영역인 __BoundingBox__ 내에서 __EquipmentDetections__ 내용이 없으면 그 영역을 검출.

- 마스크 착용은 했지만 올바르지 않은 착용인 모습이면(ex: 코스크, 턱스크) 검출.

- 위의 두가지 조건문에 해당하지 않은 사람이면 마스크 착용중인 것으로 인식한다.

![mask_2_BoundingBox](mask_2_BoundingBox.png)

- 해당 이미지에서  __Persons__ 이 검출된 영역과 __FACE_COVER__ 가 검출된 영역을 확인

- (사진 출처 : https://m.health.chosun.com/svc/news_view.html?contid=2020021203075)

```python
size = image.size

x1 = size[0] * BoundingBox['Left']
y1 = size[1] * BoundingBox['Top']
x2 = x1 + size[0] * BoundingBox['Width']
y2 = y1 + size[1] * BoundingBox['Height']

image.crop((x1,y1,x2,y2))
```
- 입력된 이미지에서 __BoundingBox__ 의 좌표값을 가지고 __crop__ 을 이용하여 이미지를 분할한다.

```python
#사진 저장
image_file_name = image_file[:-4] + "_Det" +str(num) + file_extension
croppedImage.save(image_file_name)

file_upload(bucket, image_file_name)
```
- 분할된 이미지는 로컬 컴퓨터와 bucket에 각각 저장한다.

## 개발 결과물 소개 및 실행 결과
----------------------------------
### 프로젝트 개발 결과 코드 및 다이어그램
[프로그램 코드 링크:mask_detected_program.py](https://github.com/jaeseonglee/Cloud_Computing_Term_Project/blob/main/CloudComputing_project.py)

![Diagram](Diagram.png)

### 개발 결과물 및 사진 검출 결과
<img src="object1.png" alt="object1" width="50%" height="50%"/>

#### object1.png
- 위 사진에 대해 분석 실행
- (사진 출처 : 대한민국 정부 홈페이지)

#### IDLE에서 코드를 실행한 모습
![object1_detecting](object1_detecting.png)

#### 검출되어 분할된 이미지
<img src="object1_Det1.png" alt="object1_Det1" width="30%" height="30%"/>   __object1_Det1.png__ <img src="object1_Det2.png" alt="object1_Det2" width="30%" height="30%"/>__object1_Det2.png__

#### 버킷에 저장된 이미지
<img src="cc_image.png" alt="cc_image" width="50%" height="50%"/><img src="cc_result.png" alt="cc_result" width="50%" height="50%"/>

## 개발 결과물의 필요성 및 활용방안
- SW의 필요성
    - 코로나 19 사태가 확산되어 __마스크 의무화__ 까지 생겼음에도 불구하고, 여전히 마스크를 쓰지 않는 사람들이 있습니다. 
    - 의도적으로 마스크를 착용하지 않는 사람들에게 경각심을 심어주기 위해서, 사용할 필요성이 있다고 생각합니다.
- 활용방안
    - 마스크 의무화에 반하는 사람들을 신고함에 따라 벌금형이 주어집니다.
    - 위 프로그램을 이용하여 해당 인원들의 얼굴과 인상착의를 저장하며, 벌금을 부여할 시 마스크 착용여부를 판별할 수 있는 확실한 증거로 사용될 것입니다.
     
