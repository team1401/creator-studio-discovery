"""Preserve retrieved YouTube source and try independent public metadata/captions."""
from pathlib import Path
import json, re, hashlib, datetime
import requests
from youtube_transcript_api import YouTubeTranscriptApi
ROOT = Path(__file__).resolve().parent
source = Path('/home/helix/.hermes-minimal/cache/web/www.youtube.com-c40744a697.md').read_text()
(ROOT / 'youtube-page.md').write_text(source)
transcript = source.split('### Transcript\n', 1)[1]
(ROOT / 'transcript-webextract.txt').write_text(transcript)
segments = []
for line in transcript.splitlines():
    match = re.match(r'\[(\d+):(\d+)\] (.*)', line)
    if match:
        m,s,text = match.groups()
        segments.append({'start':int(m)*60+int(s),'text':text})
(ROOT / 'transcript-webextract.json').write_text(json.dumps(segments,indent=2))
metadata = {'video_id':'5y407oZ26r0','url':'https://www.youtube.com/watch?v=5y407oZ26r0','title':source.splitlines()[0][2:],'channel':'DIGITAL INCOME PROJECT','posted_date_from_extraction':'2026-04-21','retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'provenance':'web_extract YouTube page; full cached text preserved verbatim; not audiovisual verification','segments':len(segments),'last_segment_start_seconds':segments[-1]['start'],'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
try:
    r=requests.get('https://www.youtube.com/oembed',params={'url':metadata['url'],'format':'json'},timeout=25)
    r.raise_for_status()
    metadata['oembed']=r.json()
except Exception as e:
    metadata['oembed_error']=str(e)
try:
    fetched=YouTubeTranscriptApi().fetch('5y407oZ26r0',languages=['en'])
    (ROOT / 'transcript-api.json').write_text(json.dumps(fetched.to_raw_data(),indent=2))
    metadata['transcript_api']={'status':'success','language':fetched.language,'is_generated':fetched.is_generated}
except Exception as e:
    metadata['transcript_api']={'status':'failed','error':str(e)}
(ROOT / 'metadata.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2))
print('Arithmetic check:',100_000_000*0.001,100_000_000*0.0001,10_000*9)
