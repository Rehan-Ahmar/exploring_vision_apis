import json
import os
import re
from collections import defaultdict
import copy


def load_json(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data
    
def load_amazon_response(input_filename, aws_json_path):
    return load_json(aws_json_path) 


def get_google_response(input_filename, google_json_dir):
    output = {'shots' : []}
    
    shotchange_json = load_json(os.path.join(google_json_dir, 'FRIENDS - Hulu (Japan)_shotchange.json'))
    logo_json = load_json(os.path.join(google_json_dir, 'FRIENDS - Hulu (Japan)_logo.json'))
    celebrity_json = load_json(os.path.join(google_json_dir, 'FRIENDS - Hulu (Japan)_celebrity.json'))
    
    detected_logos = []
    for logo_recognition_annotation in logo_json.get('annotation_results')[0].get('logo_recognition_annotations'):
        entity = logo_recognition_annotation.get('entity')
        # All logo tracks where the recognized logo appears. Each track corresponds to one logo instance appearing in consecutive frames.
        for track in logo_recognition_annotation.get('tracks'):
            segment = track.get('segment')
            
            logo_start_time = (segment.get('start_time_offset').get('seconds', 0) + segment.get('start_time_offset').get('nanos', 0) / 1e9)
            logo_end_time = (segment.get('end_time_offset').get('seconds', 0) + segment.get('end_time_offset').get('nanos', 0) / 1e9)
            logo_confidence = track.get('confidence')
            
            temp_logo_dict = {'entity':entity, 'logo_start_time':logo_start_time, 'logo_end_time':logo_end_time, 'logo_confidence':logo_confidence }
            detected_logos.append(temp_logo_dict)
      
    detected_celebrities = []
    for celebrity_track in celebrity_json.get('annotation_results')[0].get('celebrity_recognition_annotations').get('celebrity_tracks'):
        print(celebrity_track)
        print('*********************************')
        if not celebrity_track.get('celebrities'):
            continue
        temp = celebrity_track.get('celebrities')[0]
        celebrity = temp.get('celebrity')
        celeb_confidence = temp.get('confidence')
        segment = celebrity_track.get('face_track').get('segment')
        celeb_start_time = (segment.get('start_time_offset').get('seconds', 0) + segment.get('start_time_offset').get('nanos', 0) / 1e9)
        celeb_end_time = (segment.get('end_time_offset').get('seconds', 0) + segment.get('end_time_offset').get('nanos', 0) / 1e9)
        temp_dict_celeb = {'celebrity':celebrity, 'celeb_start_time':celeb_start_time, 'celeb_end_time':celeb_end_time, 'celeb_confidence':celeb_confidence}
        detected_celebrities.append(temp_dict_celeb)
        
    
    for i, shot in enumerate(shotchange_json.get('annotation_results')[0].get('shot_annotations')):
        start_time = (shot.get('start_time_offset').get('seconds', 0) + shot.get('start_time_offset').get('nanos', 0) / 1e9)
        end_time = (shot.get('end_time_offset').get('seconds', 0) + shot.get('end_time_offset').get('nanos', 0) / 1e9)
        print('\tShot {}: {} to {}'.format(i, start_time, end_time))
        temp_dict = {'shot_num':i, 'start_time': start_time, 'end_time': end_time, 'logos':[], 'celebrities': []}
        
        for logo in detected_logos:
            if logo['logo_start_time']>=start_time and logo['logo_end_time']<=end_time:
                temp_dict['logos'].append({'entity':logo['entity'], 'confidence': logo['logo_confidence']})
        
        for celeb in detected_celebrities:
            if celeb['celeb_start_time']>=start_time and celeb['celeb_end_time']<=end_time:
                temp_dict['celebrities'].append({'celebrity': celeb['celebrity'], 'confidence': celeb['celeb_confidence']})
        output['shots'].append(temp_dict)
        
        
    output_path = './out.json'
    with open(output_path, "w") as write_file:
        json.dump(output, write_file, indent=4)
    
        

def process_video_file(filename, aws_json_path, google_json_dir, out_json_path):
    aws_response = load_amazon_response(filename, aws_json_path)
    print(aws_response)
    #output_path = os.path.join(output_dir, doc_name +'.json')
    with open(out_json_path, "w") as write_file:
        json.dump(aws_response, write_file, indent=4)

if __name__ == '__main__':
    #process_video_file(filename='./inputs/FRIENDS - Hulu (Japan).mov', \
    #                   aws_json_path='./inputs/Amazon/FRIENDS_Hulu_Japan.json', google_json_dir='./inputs/Google/',  \
    #                   out_json_path='./out.json')
                       
    get_google_response(input_filename='./inputs/FRIENDS - Hulu (Japan).mov', google_json_dir='./inputs/Google/')
