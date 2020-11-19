#Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import cv2
import json

def detect_faces(photo, bucket):

    client=boto3.client('rekognition')

  
    #imageBytes = cv2.imencode(".jpg")


    response = client.detect_protective_equipment(
        Image={
            'S3Object':{
                'Bucket':bucket,
                'Name':photo}
            },
        SummarizationAttributes={
            'MinConfidence':80,
            'RequiredEquipmentTypes':[
                'FACE_COVER'#, 'HAND_COVER', 'HEAD_COVER'
                ]
            }
        )

    
    print('Detected faces for ' + photo)
    print("\n\n" + str(response))

    
    
    
    
    """
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low']) 
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))
    return len(response['FaceDetails'])
    """

def main():

    photo='1111.jpg'
    bucket='bucket20201117'
    
    face_count=detect_faces(photo, bucket)
    #print("Faces detected: " + str(face_count))


if __name__ == "__main__":
    main()
