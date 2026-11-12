import json
from pathlib import Path
from PIL import Image
root=Path(__file__).parent
source=root.parent/'网站制作资料包-20261005'
for sub in ['assets','content','scripts','docs','evidence']: (root/sub).mkdir(exist_ok=True)
records=json.loads((source/'项目内容资料库.json').read_text())['records']
images=json.loads((source/'精选图片登记.json').read_text())
chosen=['IMG01','IMG02','IMG05','IMG07','IMG10','IMG12','IMG13','IMG14','IMG16']
registry=[]
for item in images:
 if item['id'] not in chosen: continue
 with Image.open(item['local_copy']) as im:
  im=im.convert('RGB'); im.thumbnail((1600,1600)); dest=root/'assets'/(item['id'].lower()+'.webp'); im.save(dest,'WEBP',quality=84)
 registry.append({'id':item['id'],'project':item['project_id'],'source':item['local_copy'],'original_sha256':item['sha256'],'output':str(dest),'dimensions':list(im.size),'caution':item['caution'],'permission':'UNKNOWN; internal preview only'})
(root/'docs/asset-register.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2))
labels={'P02':'客户参与 · 交付待核','P03':'客户参与 · 交付待核','P04':'客户参与 · 交付待核','P05':'客户参与 · 交付待核','P36':'客户参与 · 工程待定位','P06':'L0 Mock 交互验证','P07':'静态前台预览','P09':'虚拟库存试点','P10':'ERP 试部署 · 业务待验','P11':'独立概念预览','P12':'本地工作台 · 内容链路待验','P13':'原生迭代 · 历史提交记录','P14':'原生实践 · 历史审核记录','P15':'封闭 Beta · Demo 图片','P16':'模拟器 MVP','P17':'阅读原型','P18':'能力实验 · 可靠性未通过','P19':'交互原型','P20':'L0 概念页'}
thumbs={'P02':'IMG01','P03':'IMG02','P07':'IMG05','P09':'IMG07','P12':'IMG10','P13':'IMG13','P14':'IMG14','P15':'IMG16'}
shortnames={'P02':'公益基金会官网','P03':'律师事务所官网','P04':'律所 OA 系统','P05':'OtherWater 全域营销','P06':'AI 录单','P07':'WilliamRock','P09':'扫码库存','P12':'织境','P13':'Pocket Rove','P14':'Focumi','P15':'PetSocial','P36':'OtherWater RAG 客服'}
intros={'P06':'先验证单据字段和人工审核，再讨论自动识别。','P07':'让产品、工厂与品牌信息更容易被理解。','P09':'围绕出入库、移库与纠错，验证库存操作闭环。','P12':'从产品事实到可审核内容，探索本地工作台的流程。','P13':'用每日小任务，为日常留一点探索空间。','P14':'把宠物陪伴放进专注流程，探索更温和的行动体验。','P15':'以宠物为起点，探索发现、连接与聊天的体验。'}
out=[]
for r in records:
 category='客户参与' if r['id'] in ['P02','P03','P04','P05','P36'] else '网站与工具' if r['id'] in ['P06','P07','P08','P09','P10','P11','P12','P20'] else 'App 实践' if r['id'] in ['P13','P14','P15','P16','P17','P18','P19','P25','N01'] else '内容与研究' if r['group'] in ['自动化与研究','设计与内容','学习与研究','进行中的学习研究'] else '方法与支持'
 out.append({'id':r['id'],'name':shortnames.get(r['id'],r['name']),'fullName':r['name'],'category':category,'label':labels.get(r['id'],'研究与实践记录'),'intro':intros.get(r['id'],r['problem']),'work':r['work'],'evidence':r['proof'],'boundary':r['boundary'],'status':r['status'],'experience':r['transferable_experience'],'image':thumbs.get(r['id']),'personalRole':'本人确认参与；个人模块与团队分工待补。' if category=='客户参与' else '项目实践记录；具体个人贡献与协作分工待确认。','publicReady':False})
(root/'content/projects.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(root/'content/profile.json').write_text(json.dumps({'displayName':None,'email':None,'avatar':None,'headline':'从真实问题，\n到可用体验。','intro':'我借助 AI 协作，把业务需求逐步转化为网站、工具和应用。这里记录我的参与经历、产品实践与持续学习。','about':'2026 年 5 月至 8 月，我在原点向量参与技术支持相关工作，涉及网站前后端、运营维护和测试。此后持续探索 AI 协作开发、企业业务工具与个人产品。','personality':'我偏内向，比较慢热。比起给自己贴很多标签，我更愿意从做过的事开始介绍自己。','background':'我并非传统程序员出身，主要通过项目实践和 AI agent 辅助积累知识。能力还在成长，具体工作与成果以案例为准。'},ensure_ascii=False,indent=2))
print('Created sanitized content for',len(out),'records and',len(registry),'preview images')
