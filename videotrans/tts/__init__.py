import os
import threading
from videotrans.configure import config
from videotrans.util import tools

# 文字合成
def text_to_speech(inst=None,*,text="", role="", rate='+0%',language=None, filename=None, tts_type=None, play=False, set_p=True,is_test=False,btnkey=None):
    try:
        if tts_type == "edgeTTS":
            from .edgetts import get_voice
            get_voice(text=text, role=role, rate=rate, language=language,filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type == "AzureTTS":
            from .azuretts import get_voice
            get_voice(text=text, role=role, rate=rate, language=language,filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type == "openaiTTS":
            from .openaitts import get_voice
            get_voice(text=text, role=role, rate=rate, filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type == "clone-voice":
            from .clone import get_voice
            get_voice(text=text, role=role, language=language, filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type=='TTS-API':
            from .ttsapi import get_voice
            get_voice(text=text, role=role, language=language, filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type=='GPT-SoVITS':
            from .gptsovits import get_voice
            get_voice(text=text, role=role, language=language, filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        elif tts_type == 'elevenlabsTTS':
            from .elevenlabs import get_voice
            get_voice(text=text, role=role, rate=rate, filename=filename,set_p=set_p,is_test=is_test,inst=inst)
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            if play:
                threading.Thread(target=tools.pygameaudio, args=(filename,)).start()
            return True
        else:
            config.logger.error(f'no filename={filename} {tts_type=} {text=},{role=}')
            return False
    except Exception as e:
        err=str(e)
        raise Exception(f'text->speech:{err}')


def run(*, queue_tts=None, language=None,set_p=True,inst=None):
    def get_item(q):
        return {"text": q['text'], "role": q['role'], "rate": q["rate"],
                "filename": q["filename"], "tts_type": q['tts_type'],
                "language":language

                }

    # 需要并行的数量3
    n_total = len(queue_tts)
    if n_total<1:
        raise Exception(f'[error]queue_tts length < 1')
    n = 0
    dub_nums=config.settings['dubbing_thread']
    while len(queue_tts) > 0:
        if config.current_status != 'ing' and config.box_tts != 'ing':
            raise Exception('stop')
        try:
            tolist = []
            for i in range(dub_nums):
                if len(queue_tts) > 0:
                    p=get_item(queue_tts.pop(0))
                    if p['tts_type']!='clone-voice' and os.path.exists(p['filename']) and os.path.getsize(p['filename'])>0:
                        continue
                    p["set_p"]=set_p
                    p['inst']=inst
                    tolist.append(threading.Thread(target=text_to_speech, kwargs=p))
            if len(tolist)<1:
                continue
            for t in tolist:
                t.start()
            for t in tolist:
                # n += 1
                # if set_p:
                #     if inst and inst.precent<90:
                #         inst.precent+=round(n/n_total,2)
                #     tools.set_process(f'{config.transobj["kaishipeiyin"]} [{n}/{n_total}]',btnkey=inst.btnkey)
                t.join()
        except Exception as e:
            raise Exception(f'runtts:{str(e)}')
    return True
