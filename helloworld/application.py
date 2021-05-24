#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
from flask_cors import CORS
import boto3


application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/calc/bit', methods=['GET'])
def post_currency_bit():
    return Response(json.dumps(get_bitcoin_index()), mimetype='application/json', status=200)


def get_bitcoin_index():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url).json()['bpi']['USD']
    return response

# return generic data
@application.route('/get_generic', methods=['GET'])
def get_generic_data():
    return Response(json.dumps(generic_data), mimetype='application/json', status=200)


# get example for multiplication
# test get  
# curl -i http://"localhost:5000/v1/multiply?first_num=12.1&second_num=12"

@application.route('/v1/multiply', methods=['GET', 'POST'])
def get_mult_res():
    
    first_num = request.args.get('first_num')
    second_num = request.args.get('second_num')
    res = float(first_num) * float(second_num) 
    return Response(json.dumps({'multiplication result': res}), mimetype='application/json', status=200)




# mock data
currency_rate = {
    'usd' : 3.3,
    'pound' : 4.5,
    'euro' : 4.8
}

#generic data
generic_data = [
 
    {
    "id":1,
    "title": "wtf",
    "body": "good will"
    },
    {
    "id":2,
    "title": "wtf2",
    "body": "good will2"
    }
   ]


@application.route('/get_forms', methods=['GET'])
def get_frm():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # replace table scan
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)


# curl -i -X POST -d'{"form_title":"form title1", "form_body":"where is it?", "form_type":"finance"}' -H "Content-Type: application/json" http://localhost:5000/set_form/frm4
@application.route('/set_form/<frm_id>', methods=['POST'])
def set_doc(frm_id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    form_body = data_dict.get('form_body','default')
    form_title = data_dict.get('form_title','defualt')
    form_type = data_dict.get('form_type', 'default')

    item={
    'form_id': frm_id,
    'form_body': form_body,
    'form_title': form_title, 
    'form_type': form_type 
     }
    table.put_item(Item=item)
    
    return Response(json.dumps(item), mimetype='application/json', status=200)
    
    
@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='my-upload-bucket-01', image='person.jpg'):
    return detect_labels(bucket, image)

# curl localhost:5000/analyze/my-upload-bucket-01/person.jpg
def detect_labels(bucket, key, max_labels=10, min_confidence=50, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')

    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image

    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])

    '''
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
	'''

@application.route('/comp_face/<source_image>/<target_image>', methods=['GET'])
def compare_face(source_image, target_image):
    # change region and bucket accordingly
    region = 'us-east-1'
    bucket_name = 'my-upload-bucket-01'
	
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": target_image,
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=50,
    )
    # return 0 if below similarity threshold
    return json.dumps(response['FaceMatches'] if response['FaceMatches'] != [] else [{"Similarity": 0.0}])


if __name__ == '__main__':
    flaskrun(application)
