#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, ipaddress, json, os, shutil, socket, subprocess, tempfile, urllib.parse, urllib.request
from pathlib import Path

MAX_MANIFEST_BYTES=5*1024*1024
MAX_IMAGES=40
MAX_IMAGE_BYTES=20*1024*1024
MAX_TOTAL_IMAGE_BYTES=300*1024*1024
MAX_AUDIO_BYTES=50*1024*1024
MAX_SCENES=20
MAX_VIDEO_SECONDS=180
MAX_REDIRECTS=5
ALLOWED_HOSTS_ENV="MINA_VIDEO_ALLOWED_HOSTS"

class RenderError(RuntimeError): pass

def fail(message): raise RenderError(message)

def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:
        fail((p.stderr or p.stdout).strip()[-3000:] or 'command failed')

def require_tools():
    missing=[x for x in ('ffmpeg','ffprobe','espeak-ng') if shutil.which(x) is None]
    if missing: fail('missing tools: '+', '.join(missing))

def https_url(value,label):
    url=str(value or '').strip(); p=urllib.parse.urlparse(url)
    if p.scheme!='https' or not p.netloc or p.fragment or p.username or p.password:
        fail(f'{label} must be an HTTPS URL without fragments or embedded credentials')
    try:
        if p.port not in (None,443):
            pass
    except ValueError:
        fail(f'{label} contains an invalid port')
    return url

def canonical_endpoint(value,label):
    raw=str(value or '').strip()
    if not raw:
        fail(f'{label} is empty')
    parsed=urllib.parse.urlparse('https://' + raw)
    if parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        fail(f'{label} must be a hostname with an optional port')
    try:
        host=parsed.hostname
        port=parsed.port
    except ValueError:
        fail(f'{label} contains an invalid port')
    if not host:
        fail(f'{label} must contain a hostname')
    try:
        host=host.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        fail(f'{label} contains an invalid hostname')
    return f'{host}:{port or 443}'

def canonical_url_endpoint(url,label):
    parsed=urllib.parse.urlparse(https_url(url,label))
    try:
        host=parsed.hostname
        port=parsed.port
    except ValueError:
        fail(f'{label} contains an invalid port')
    if not host:
        fail(f'{label} must contain a hostname')
    try:
        host=host.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        fail(f'{label} contains an invalid hostname')
    return f'{host}:{port or 443}'

def reject_private_resolution(url,label):
    parsed=urllib.parse.urlparse(url)
    host=parsed.hostname
    if not host:
        fail(f'{label} must contain a hostname')
    try:
        infos=socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        fail(f'{label} DNS resolution failed: {exc}')
    addresses={info[4][0] for info in infos}
    if not addresses:
        fail(f'{label} DNS returned no addresses')
    for address in addresses:
        try:
            ip=ipaddress.ip_address(address)
        except ValueError:
            fail(f'{label} resolved to an invalid IP address')
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            fail(f'{label} resolves to a non-public IP address: {address}')

def approved_asset_url(value,label):
    url=https_url(value,label)
    configured=os.environ.get(ALLOWED_HOSTS_ENV,'')
    if not configured.strip():
        fail(f'{ALLOWED_HOSTS_ENV} is not configured; production asset downloads are fail-closed')
    allowed={canonical_endpoint(item,f'{ALLOWED_HOSTS_ENV} entry') for item in configured.split(',') if item.strip()}
    if not allowed:
        fail(f'{ALLOWED_HOSTS_ENV} contains no usable hosts')
    endpoint=canonical_url_endpoint(url,label)
    if endpoint not in allowed:
        fail(f'{label} host is not approved for production: {endpoint}')
    reject_private_resolution(url,label)
    return url

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download(url,target,max_bytes):
    current=approved_asset_url(url,'asset URL')
    opener=urllib.request.build_opener(_NoRedirect)
    for _ in range(MAX_REDIRECTS + 1):
        current=approved_asset_url(current,'asset URL')
        req=urllib.request.Request(current,headers={'User-Agent':'mina-video-runner/1'})
        try:
            response=opener.open(req,timeout=30)
        except urllib.error.HTTPError as exc:
            if exc.code in {301,302,303,307,308}:
                location=exc.headers.get('Location')
                if not location: fail(f'redirect without Location: {current}')
                current=approved_asset_url(urllib.parse.urljoin(current,location),'redirect URL')
                continue
            raise
        with response:
            length=response.headers.get('Content-Length')
            if length and int(length)>max_bytes: fail(f'asset exceeds size limit: {current}')
            total=0
            with target.open('wb') as out:
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk: break
                    total+=len(chunk)
                    if total>max_bytes: fail(f'asset exceeds size limit: {current}')
                    out.write(chunk)
            return total
    fail(f'too many redirects: {url}')

def sha256(path):
    d=hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024*1024),b''): d.update(chunk)
    return d.hexdigest()

def duration(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],capture_output=True,text=True)
    if p.returncode: fail(p.stderr.strip() or 'unable to probe media')
    try: return float(p.stdout.strip())
    except ValueError: fail('invalid media duration')

def render_scene(root,scene,index,voice):
    narration=str(scene.get('narration','')).strip()
    if not narration: fail(f'scene {index}: narration is required')
    images=scene.get('images')
    if not isinstance(images,list) or not images: fail(f'scene {index}: at least one image is required')
    if len(images)>6: fail(f'scene {index}: maximum 6 images')
    scene_dir=root/f'scene-{index}'; scene_dir.mkdir()
    image_paths=[]; scene_image_bytes=0
    for n,item in enumerate(images,1):
        path=scene_dir/f'image-{n}.bin'
        scene_image_bytes += download(item,path,MAX_IMAGE_BYTES)
        image_paths.append(path)
    audio=scene_dir/'audio.wav'
    audio_url=str(scene.get('audio_url','')).strip()
    if audio_url: download(audio_url,audio,MAX_AUDIO_BYTES)
    else:
        selected_voice=voice if voice in {'en','ar'} else 'en'
        run(['espeak-ng','-v',selected_voice,'-s','145' if selected_voice=='ar' else '155','-w',str(audio),narration])
    dur=max(1.0,duration(audio))
    if dur>60: fail(f'scene {index}: duration exceeds 60 seconds')
    caption=root/f'caption-{index}.txt'; caption.write_text(narration[:1000],encoding='utf-8')
    per_image=max(1.5,dur/len(image_paths)); clips=[]
    for n,image in enumerate(image_paths,1):
        clip=scene_dir/f'clip-{n}.mp4'; frames=max(45,int(per_image*30))
        vf=('scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
            f"zoompan=z='min(zoom+0.0007,1.06)':d={frames}:s=1080x1920:fps=30,format=yuv420p,"
            'fade=t=in:st=0:d=0.15,'
            f'fade=t=out:st={max(per_image-0.15,0):.3f}:d=0.15')
        run(['ffmpeg','-y','-loop','1','-i',str(image),'-t',f'{per_image:.3f}','-vf',vf,'-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(clip)])
        clips.append(clip)
    concat=scene_dir/'images.txt'; concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clips),encoding='utf-8')
    silent=scene_dir/'silent.mp4'
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-t',f'{dur:.3f}','-c','copy',str(silent)])
    final_scene=root/f'scene-{index}.mp4'
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    vf=f"drawtext=fontfile={font}:textfile='{caption.as_posix()}':fontcolor=white:fontsize=52:line_spacing=12:x=(w-text_w)/2:y=h-430:box=1:boxcolor=black@0.58:boxborderw=28"
    run(['ffmpeg','-y','-i',str(silent),'-i',str(audio),'-vf',vf,'-map','0:v:0','-map','1:a:0','-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-af','loudnorm=I=-16:LRA=11:TP=-1.5','-shortest','-movflags','+faststart',str(final_scene)])
    return final_scene, scene_image_bytes

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
    require_tools(); raw=Path(args.manifest).read_bytes()
    if len(raw)>MAX_MANIFEST_BYTES: fail('manifest is too large')
    try: manifest=json.loads(raw.decode('utf-8'))
    except Exception as exc: fail(f'invalid JSON manifest: {exc}')
    if not isinstance(manifest,dict) or manifest.get('schema')!='external-video/v1': fail('unsupported manifest schema')
    scenes=manifest.get('scenes')
    if not isinstance(scenes,list) or not scenes or len(scenes)>MAX_SCENES: fail('scenes must contain 1..20 items')
    total_images=sum(len(s.get('images',[])) for s in scenes if isinstance(s,dict) and isinstance(s.get('images'),list))
    if total_images>MAX_IMAGES: fail('manifest image limit exceeded')
    voice=str(manifest.get('voice','en')).lower()
    total_image_bytes=0
    with tempfile.TemporaryDirectory(prefix='mina-video-') as temp:
        root=Path(temp); clips=[]
        for i,s in enumerate(scenes,1):
            clip, image_bytes=render_scene(root,s,i,voice)
            total_image_bytes += image_bytes
            if total_image_bytes>MAX_TOTAL_IMAGE_BYTES: fail('total image download limit exceeded')
            clips.append(clip)
        concat=root/'scenes.txt'; concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clips),encoding='utf-8')
        output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(output)])
    dur=duration(Path(args.output))
    if dur<=0 or dur>MAX_VIDEO_SECONDS: fail(f'final duration outside allowed range: {dur:.2f}s')
    print(json.dumps({'status':'RENDERED','output':str(Path(args.output)),'sha256':sha256(Path(args.output)),'duration_seconds':round(dur,3)}))

if __name__=='__main__':
    try: main()
    except RenderError as exc: print(f'ERROR: {exc}',file=__import__('sys').stderr); raise SystemExit(2)
